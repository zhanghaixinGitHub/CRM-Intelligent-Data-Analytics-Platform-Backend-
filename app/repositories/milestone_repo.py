"""履约里程碑数据访问层。"""

from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import FulfillmentMilestone
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate


class MilestoneRepository:
    """履约里程碑仓储类（Repository Pattern）。"""

    @staticmethod
    def list_by_fulfill(db: Session, fulfill_id: int) -> list[FulfillmentMilestone]:
        stmt = select(FulfillmentMilestone).where(FulfillmentMilestone.fulfill_id == fulfill_id).order_by(FulfillmentMilestone.id.desc())
        return list(db.scalars(stmt))

    @staticmethod
    def create(db: Session, payload: MilestoneCreate) -> FulfillmentMilestone:
        obj = FulfillmentMilestone(**payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def update(db: Session, milestone_id: int, payload: MilestoneUpdate) -> FulfillmentMilestone | None:
        obj = db.get(FulfillmentMilestone, milestone_id)
        if not obj:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def list_overdue(db: Session) -> list[FulfillmentMilestone]:
        today_str = date.today().isoformat()
        stmt = (
            select(FulfillmentMilestone)
            .where(FulfillmentMilestone.status != "完成")
            .where(FulfillmentMilestone.due_date != "")
            .where(FulfillmentMilestone.due_date < today_str)
            .order_by(FulfillmentMilestone.due_date.asc())
        )
        return list(db.scalars(stmt))

