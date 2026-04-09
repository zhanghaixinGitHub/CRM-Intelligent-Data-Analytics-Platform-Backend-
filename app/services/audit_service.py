"""审计服务层。"""

from sqlalchemy.orm import Session
from app.repositories.audit_repo import AuditRepository


class AuditService:
    """审计服务（Facade Pattern 对外统一入口）。"""

    @staticmethod
    def log(
        db: Session,
        module: str,
        action: str,
        user: dict,
        target_id: str,
        detail: str,
    ) -> None:
        AuditRepository.create(
            db=db,
            module=module,
            action=action,
            operator=user.get("name", "系统"),
            role=user.get("role", "admin"),
            target_id=target_id,
            detail=detail,
        )

