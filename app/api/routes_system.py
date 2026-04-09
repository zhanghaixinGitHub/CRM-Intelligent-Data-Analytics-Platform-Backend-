"""系统路由。"""

import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.auth import ensure_min_role, get_current_user
from app.core.database import get_db
from app.repositories.audit_repo import AuditRepository
from app.schemas.common import ApiResponse
from app.services.concurrency_service import ConcurrencyService

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/concurrency-test", response_model=ApiResponse)
def concurrency_test(
    workers: int = Query(default=20, ge=1, le=200),
    tasks: int = Query(default=100, ge=1, le=2000),
) -> ApiResponse:
    """并发锁测试接口。"""
    result = ConcurrencyService.run_test(workers=workers, tasks=tasks)
    return ApiResponse(data=result)


@router.get("/audit-logs", response_model=ApiResponse)
def list_audit_logs(
    module: str | None = Query(default=None),
    operator: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse:
    """查询操作审计日志。"""
    try:
        ensure_min_role(user, "manager")
    except HTTPException as exc:
        raise exc
    rows, total = AuditRepository.list_rows(db, module=module, operator=operator, page=page, page_size=page_size)
    data = [
        {
            "id": item.id,
            "module": item.module,
            "action": item.action,
            "operator": item.operator,
            "role": item.role,
            "target_id": item.target_id,
            "detail": item.detail,
            "created_at": item.created_at,
        }
        for item in rows
    ]
    return ApiResponse(data={"items": data, "total": total, "page": page, "page_size": page_size})


@router.get("/audit-logs/export.csv")
def export_audit_logs(
    module: str | None = Query(default=None),
    operator: str | None = Query(default=None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """导出审计日志CSV。"""
    ensure_min_role(user, "manager")
    rows, _ = AuditRepository.list_rows(db, module=module, operator=operator, page=1, page_size=5000)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["模块", "动作", "操作人", "角色", "目标ID", "详情", "时间"])
    for item in rows:
        writer.writerow([item.module, item.action, item.operator, item.role, item.target_id, item.detail, item.created_at])
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )

