"""线索路由。"""

import csv
import io
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.auth import ensure_min_role, get_current_user
from app.core.database import get_db
from app.repositories.lead_repo import LeadRepository
from app.schemas.common import ApiResponse
from app.schemas.lead import LeadCreate, LeadUpdate
from app.services.audit_service import AuditService
from app.services.lead_service import LeadService

router = APIRouter(prefix="/api/leads", tags=["leads"])


def _to_dict(row: object) -> dict:
    """将 ORM 对象转换为纯字典，避免返回 SQLAlchemy 内部状态。"""
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


@router.get("", response_model=ApiResponse)
def list_leads(
    status: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    sort_by: str = Query(default="id"),
    sort_order: str = Query(default="desc"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse:
    owner_scope = user["name"] if user["role"] == "sales" else None
    rows, total = LeadRepository.list_leads(
        db,
        status=status,
        keyword=keyword,
        owner=owner_scope,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return ApiResponse(data={"items": [_to_dict(item) for item in rows], "total": total, "page": page, "page_size": page_size})


@router.post("", response_model=ApiResponse)
def create_lead(payload: LeadCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ApiResponse:
    row = LeadRepository.create_lead(db, payload)
    AuditService.log(db, module="lead", action="create", user=user, target_id=str(row.id), detail=f"创建线索:{row.lead_name}")
    return ApiResponse(data=_to_dict(row))


@router.put("/{lead_id}", response_model=ApiResponse)
def update_lead(lead_id: int, payload: LeadUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ApiResponse:
    row = LeadRepository.update_lead(db, lead_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="线索不存在")
    AuditService.log(db, module="lead", action="update", user=user, target_id=str(row.id), detail=f"更新线索:{row.lead_name}")
    return ApiResponse(data=_to_dict(row))


@router.post("/{lead_id}/convert-to-opportunity", response_model=ApiResponse)
def convert_to_opportunity(
    lead_id: int,
    owner: str = Query(default="系统"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse:
    """线索转商机（真实项目常见功能）。"""
    ensure_min_role(user, "manager")
    try:
        result = LeadService.convert_to_opportunity(db, lead_id, owner=owner)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not result:
        raise HTTPException(status_code=404, detail="线索不存在")
    AuditService.log(
        db,
        module="lead",
        action="convert",
        user=user,
        target_id=str(lead_id),
        detail=f"线索转商机, new_opp={result['opportunity_code']}",
    )
    return ApiResponse(data=result)


@router.post("/import-csv", response_model=ApiResponse)
async def import_csv(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse:
    """CSV 批量导入线索（轻量版，适合本地演示）。"""
    ensure_min_role(user, "manager")
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="仅支持CSV文件")
    raw = await file.read()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    created = 0
    for row in reader:
        if not row.get("lead_name"):
            continue
        payload = LeadCreate(
            lead_code=row.get("lead_code") or f"LEADIMP{created + 1:04d}",
            lead_name=row.get("lead_name", ""),
            customer_name=row.get("customer_name", ""),
            source=row.get("source", "导入"),
            region=row.get("region", "中国区"),
            product_direction=row.get("product_direction", "AR眼镜"),
            priority=row.get("priority", "中"),
            status=row.get("status", "线索录入"),
            owner=row.get("owner", user["name"]),
            contact=row.get("contact", ""),
            phone=row.get("phone", ""),
            notes=row.get("notes", ""),
        )
        LeadRepository.create_lead(db, payload)
        created += 1

    AuditService.log(
        db,
        module="lead",
        action="import_csv",
        user=user,
        target_id=file.filename,
        detail=f"导入线索数量:{created}",
    )
    return ApiResponse(data={"created": created, "filename": file.filename})


@router.get("/export.csv")
def export_leads(db: Session = Depends(get_db)) -> StreamingResponse:
    """导出线索CSV。"""
    rows, _ = LeadRepository.list_leads(db, page=1, page_size=3000, sort_by="id", sort_order="desc")
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["线索编号", "线索名称", "客户", "状态", "来源", "区域", "负责人", "转化商机编码"])
    for item in rows:
        writer.writerow(
            [
                item.lead_code,
                item.lead_name,
                item.customer_name,
                item.status,
                item.source,
                item.region,
                item.owner,
                item.converted_opportunity_code,
            ]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )

