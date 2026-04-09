"""客户路由。"""

import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.database import get_db
from app.repositories.customer_repo import CustomerRepository
from app.schemas.common import ApiResponse
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/customers", tags=["customers"])


def _to_dict(row: object) -> dict:
    """将 ORM 对象转换为纯字典，避免返回 SQLAlchemy 内部状态。"""
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


@router.get("", response_model=ApiResponse)
def list_customers(
    keyword: str | None = Query(default=None),
    grade: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    sort_by: str = Query(default="id"),
    sort_order: str = Query(default="desc"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse:
    # 权限策略：销售仅可查看本人数据；经理及以上查看全量。
    owner_scope = user["name"] if user["role"] == "sales" else None
    rows, total = CustomerRepository.list_customers(
        db,
        keyword=keyword,
        grade=grade,
        owner=owner_scope,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return ApiResponse(data={"items": [_to_dict(item) for item in rows], "total": total, "page": page, "page_size": page_size})


@router.post("", response_model=ApiResponse)
def create_customer(payload: CustomerCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ApiResponse:
    row = CustomerRepository.create_customer(db, payload)
    AuditService.log(db, module="customer", action="create", user=user, target_id=str(row.id), detail=f"创建客户:{row.customer_name}")
    return ApiResponse(data=_to_dict(row))


@router.put("/{customer_id}", response_model=ApiResponse)
def update_customer(customer_id: int, payload: CustomerUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ApiResponse:
    row = CustomerRepository.update_customer(db, customer_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="客户不存在")
    AuditService.log(db, module="customer", action="update", user=user, target_id=str(row.id), detail=f"更新客户:{row.customer_name}")
    return ApiResponse(data=_to_dict(row))


@router.get("/export.csv")
def export_customers(db: Session = Depends(get_db)) -> StreamingResponse:
    """导出客户CSV，模拟真实项目中的报表导出能力。"""
    rows, _ = CustomerRepository.list_customers(db, page=1, page_size=2000, sort_by="id", sort_order="desc")
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["客户编码", "客户名称", "等级", "区域", "行业", "负责人", "标签"])
    for item in rows:
        writer.writerow([item.customer_code, item.customer_name, item.grade, item.region, item.industry, item.owner, item.tags])
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=customers.csv"},
    )

