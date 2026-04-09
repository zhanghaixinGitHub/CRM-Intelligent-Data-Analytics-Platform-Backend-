"""商机路由。"""

import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.auth import ensure_min_role, get_current_user
from app.core.database import get_db
from app.repositories.opportunity_repo import OpportunityRepository
from app.schemas.common import ApiResponse
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate
from app.schemas.opportunity_stage import OpportunityAdvanceRequest
from app.services.audit_service import AuditService
from app.services.opportunity_service import OpportunityService

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


def _to_dict(row: object) -> dict:
    """将 ORM 对象转换为纯字典，避免返回 SQLAlchemy 内部状态。"""
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


@router.get("", response_model=ApiResponse)
def list_opportunities(
    keyword: str | None = Query(default=None),
    stage: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    sort_by: str = Query(default="id"),
    sort_order: str = Query(default="desc"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse:
    owner_scope = user["name"] if user["role"] == "sales" else None
    rows, total = OpportunityRepository.list_opportunities(
        db,
        keyword=keyword,
        stage=stage,
        owner=owner_scope,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return ApiResponse(data={"items": [_to_dict(item) for item in rows], "total": total, "page": page, "page_size": page_size})


@router.post("", response_model=ApiResponse)
def create_opportunity(payload: OpportunityCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ApiResponse:
    row = OpportunityRepository.create_opportunity(db, payload)
    AuditService.log(db, module="opportunity", action="create", user=user, target_id=str(row.id), detail=f"创建商机:{row.opp_name}")
    return ApiResponse(data=_to_dict(row))


@router.put("/{opp_id}", response_model=ApiResponse)
def update_opportunity(opp_id: int, payload: OpportunityUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ApiResponse:
    row = OpportunityRepository.update_opportunity(db, opp_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="商机不存在")
    AuditService.log(db, module="opportunity", action="update", user=user, target_id=str(row.id), detail=f"更新商机:{row.opp_name}")
    return ApiResponse(data=_to_dict(row))


@router.post("/{opp_id}/advance-stage", response_model=ApiResponse)
def advance_stage(
    opp_id: int,
    payload: OpportunityAdvanceRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse:
    """商机阶段推进接口，内置提案资料/评审门禁校验规则。"""
    ensure_min_role(user, "manager")
    try:
        result = OpportunityService.advance_stage(db, opp_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not result:
        raise HTTPException(status_code=404, detail="商机不存在")
    AuditService.log(
        db,
        module="opportunity",
        action="advance_stage",
        user=user,
        target_id=str(opp_id),
        detail=f"{result['old_stage']}->{result['new_stage']}",
    )
    return ApiResponse(data=result)


@router.get("/export.csv")
def export_opportunities(db: Session = Depends(get_db)) -> StreamingResponse:
    """导出商机CSV。"""
    rows, _ = OpportunityRepository.list_opportunities(db, page=1, page_size=3000, sort_by="id", sort_order="desc")
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["商机编码", "商机名称", "客户", "阶段", "金额", "赢率", "负责人"])
    for item in rows:
        writer.writerow([item.opp_code, item.opp_name, item.customer_name, item.stage, item.amount, item.win_rate, item.owner])
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=opportunities.csv"},
    )

