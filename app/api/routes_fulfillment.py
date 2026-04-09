"""履约路由。"""

import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.auth import ensure_min_role, get_current_user
from app.core.database import get_db
from app.repositories.fulfillment_repo import FulfillmentRepository
from app.repositories.milestone_repo import MilestoneRepository
from app.schemas.common import ApiResponse
from app.schemas.fulfillment import FulfillmentCreate, FulfillmentUpdate
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate
from app.services.audit_service import AuditService
from app.services.fulfillment_service import FulfillmentService

router = APIRouter(prefix="/api/fulfillments", tags=["fulfillments"])


def _to_dict(row: object) -> dict:
    """将 ORM 对象转换为纯字典，避免返回 SQLAlchemy 内部状态。"""
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


@router.get("", response_model=ApiResponse)
def list_fulfillments(
    stage: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    sort_by: str = Query(default="id"),
    sort_order: str = Query(default="desc"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse:
    owner_scope = user["name"] if user["role"] == "sales" else None
    rows, total = FulfillmentRepository.list_rows(
        db,
        stage=stage,
        keyword=keyword,
        owner=owner_scope,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return ApiResponse(data={"items": [_to_dict(item) for item in rows], "total": total, "page": page, "page_size": page_size})


@router.post("", response_model=ApiResponse)
def create_fulfillment(payload: FulfillmentCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ApiResponse:
    row = FulfillmentRepository.create_row(db, payload)
    AuditService.log(db, module="fulfillment", action="create", user=user, target_id=str(row.id), detail=f"创建履约:{row.project_name}")
    return ApiResponse(data=_to_dict(row))


@router.put("/{row_id}", response_model=ApiResponse)
def update_fulfillment(row_id: int, payload: FulfillmentUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ApiResponse:
    row = FulfillmentRepository.update_row(db, row_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="履约记录不存在")
    AuditService.log(db, module="fulfillment", action="update", user=user, target_id=str(row.id), detail=f"更新履约:{row.project_name}")
    return ApiResponse(data=_to_dict(row))


@router.get("/{row_id}/milestones", response_model=ApiResponse)
def list_milestones(row_id: int, db: Session = Depends(get_db)) -> ApiResponse:
    rows = MilestoneRepository.list_by_fulfill(db, row_id)
    return ApiResponse(data=[_to_dict(item) for item in rows])


@router.post("/{row_id}/milestones", response_model=ApiResponse)
def create_milestone(row_id: int, payload: MilestoneCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ApiResponse:
    ensure_min_role(user, "manager")
    if payload.fulfill_id != row_id:
        raise HTTPException(status_code=400, detail="fulfill_id与路径参数不一致")
    row = MilestoneRepository.create(db, payload)
    AuditService.log(db, module="fulfillment", action="create_milestone", user=user, target_id=str(row.id), detail=f"新增里程碑:{row.milestone_name}")
    return ApiResponse(data=_to_dict(row))


@router.put("/milestones/{milestone_id}", response_model=ApiResponse)
def update_milestone(
    milestone_id: int,
    payload: MilestoneUpdate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse:
    ensure_min_role(user, "manager")
    row = MilestoneRepository.update(db, milestone_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="里程碑不存在")
    AuditService.log(db, module="fulfillment", action="update_milestone", user=user, target_id=str(row.id), detail=f"更新里程碑:{row.milestone_name}")
    return ApiResponse(data=_to_dict(row))


@router.get("/overdue-milestones", response_model=ApiResponse)
def list_overdue_milestones(db: Session = Depends(get_db)) -> ApiResponse:
    rows = FulfillmentService.list_overdue_milestones(db)
    return ApiResponse(data=rows)


@router.get("/export.csv")
def export_fulfillments(db: Session = Depends(get_db)) -> StreamingResponse:
    rows, _ = FulfillmentRepository.list_rows(db, page=1, page_size=3000, sort_by="id", sort_order="desc")
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["履约编号", "项目名称", "客户", "阶段", "进度", "金额", "交付日期", "风险等级", "负责人"])
    for item in rows:
        writer.writerow([item.fulfill_code, item.project_name, item.customer_name, item.stage, item.progress, item.amount, item.delivery_date, item.risk_level, item.owner])
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=fulfillments.csv"},
    )

