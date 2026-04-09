"""看板聚合查询层。"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.entities import Opportunity


class DashboardRepository:
    """看板仓储类。"""

    @staticmethod
    def summary_amount(db: Session) -> float:
        total = db.scalar(select(func.sum(Opportunity.amount)))
        return float(total or 0.0)

    @staticmethod
    def stage_totals(db: Session) -> dict[str, float]:
        rows = db.execute(
            select(Opportunity.stage, func.sum(Opportunity.amount))
            .group_by(Opportunity.stage)
            .order_by(Opportunity.stage)
        ).all()
        return {stage: float(total or 0.0) for stage, total in rows}

