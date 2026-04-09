"""履约服务层。"""

from sqlalchemy.orm import Session
from app.repositories.milestone_repo import MilestoneRepository


class FulfillmentService:
    """
    履约服务类（Service Pattern）。
    负责里程碑预警等跨数据处理逻辑。
    """

    @staticmethod
    def list_overdue_milestones(db: Session) -> list[dict]:
        rows = MilestoneRepository.list_overdue(db)
        return [
            {
                "id": row.id,
                "fulfill_id": row.fulfill_id,
                "milestone_name": row.milestone_name,
                "due_date": row.due_date,
                "status": row.status,
                "owner": row.owner,
                "warning_level": "高",
                "notes": row.notes,
            }
            for row in rows
        ]

