"""线索数据访问层。"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.entities import Lead
from app.schemas.lead import LeadCreate, LeadUpdate


class LeadRepository:
    """
    线索仓储类（Repository Pattern）。
    通过仓储层隔离 ORM 细节，便于后续切换数据源或扩展复杂查询。
    """

    @staticmethod
    def get_by_id(db: Session, lead_id: int) -> Lead | None:
        return db.get(Lead, lead_id)

    @staticmethod
    def list_leads(
        db: Session,
        status: str | None = None,
        keyword: str | None = None,
        owner: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "id",
        sort_order: str = "desc",
    ) -> tuple[list[Lead], int]:
        stmt = select(Lead)
        count_stmt = select(func.count()).select_from(Lead)
        if status:
            stmt = stmt.where(Lead.status == status)
            count_stmt = count_stmt.where(Lead.status == status)
        if keyword:
            stmt = stmt.where(Lead.lead_name.contains(keyword))
            count_stmt = count_stmt.where(Lead.lead_name.contains(keyword))
        if owner:
            stmt = stmt.where(Lead.owner == owner)
            count_stmt = count_stmt.where(Lead.owner == owner)

        sort_col = getattr(Lead, sort_by, Lead.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(sort_col.asc())
        else:
            stmt = stmt.order_by(sort_col.desc())

        total = int(db.scalar(count_stmt) or 0)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        return list(db.scalars(stmt)), total

    @staticmethod
    def create_lead(db: Session, payload: LeadCreate) -> Lead:
        obj = Lead(**payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def update_lead(db: Session, lead_id: int, payload: LeadUpdate) -> Lead | None:
        obj = db.get(Lead, lead_id)
        if not obj:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

