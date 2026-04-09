"""审计日志数据访问层。"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.entities import AuditLog


class AuditRepository:
    """审计日志仓储类。"""

    @staticmethod
    def create(
        db: Session,
        module: str,
        action: str,
        operator: str,
        role: str,
        target_id: str,
        detail: str,
    ) -> AuditLog:
        row = AuditLog(
            module=module,
            action=action,
            operator=operator,
            role=role,
            target_id=target_id,
            detail=detail,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def list_rows(
        db: Session,
        module: str | None = None,
        operator: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        stmt = select(AuditLog)
        count_stmt = select(func.count()).select_from(AuditLog)
        if module:
            stmt = stmt.where(AuditLog.module == module)
            count_stmt = count_stmt.where(AuditLog.module == module)
        if operator:
            stmt = stmt.where(AuditLog.operator.contains(operator))
            count_stmt = count_stmt.where(AuditLog.operator.contains(operator))
        stmt = stmt.order_by(AuditLog.id.desc()).offset((page - 1) * page_size).limit(page_size)
        total = int(db.scalar(count_stmt) or 0)
        return list(db.scalars(stmt)), total

