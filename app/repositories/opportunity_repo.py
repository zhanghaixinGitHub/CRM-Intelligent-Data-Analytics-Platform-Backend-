"""商机数据访问层。"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.entities import Opportunity
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate


class OpportunityRepository:
    """商机仓储类（Repository Pattern）。"""

    @staticmethod
    def list_opportunities(
        db: Session,
        keyword: str | None = None,
        stage: str | None = None,
        owner: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "id",
        sort_order: str = "desc",
    ) -> tuple[list[Opportunity], int]:
        stmt = select(Opportunity)
        count_stmt = select(func.count()).select_from(Opportunity)
        if keyword:
            stmt = stmt.where(Opportunity.opp_name.contains(keyword))
            count_stmt = count_stmt.where(Opportunity.opp_name.contains(keyword))
        if stage:
            stmt = stmt.where(Opportunity.stage == stage)
            count_stmt = count_stmt.where(Opportunity.stage == stage)
        if owner:
            stmt = stmt.where(Opportunity.owner == owner)
            count_stmt = count_stmt.where(Opportunity.owner == owner)

        sort_col = getattr(Opportunity, sort_by, Opportunity.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(sort_col.asc())
        else:
            stmt = stmt.order_by(sort_col.desc())

        total = int(db.scalar(count_stmt) or 0)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        return list(db.scalars(stmt)), total

    @staticmethod
    def create_opportunity(db: Session, payload: OpportunityCreate) -> Opportunity:
        obj = Opportunity(**payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def update_opportunity(db: Session, opp_id: int, payload: OpportunityUpdate) -> Opportunity | None:
        obj = db.get(Opportunity, opp_id)
        if not obj:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

