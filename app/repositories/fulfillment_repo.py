"""履约数据访问层。"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.entities import Fulfillment
from app.schemas.fulfillment import FulfillmentCreate, FulfillmentUpdate


class FulfillmentRepository:
    """履约仓储类（Repository Pattern）。"""

    @staticmethod
    def list_rows(
        db: Session,
        stage: str | None = None,
        keyword: str | None = None,
        owner: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "id",
        sort_order: str = "desc",
    ) -> tuple[list[Fulfillment], int]:
        stmt = select(Fulfillment)
        count_stmt = select(func.count()).select_from(Fulfillment)
        if stage:
            stmt = stmt.where(Fulfillment.stage == stage)
            count_stmt = count_stmt.where(Fulfillment.stage == stage)
        if keyword:
            stmt = stmt.where(Fulfillment.project_name.contains(keyword))
            count_stmt = count_stmt.where(Fulfillment.project_name.contains(keyword))
        if owner:
            stmt = stmt.where(Fulfillment.owner == owner)
            count_stmt = count_stmt.where(Fulfillment.owner == owner)

        sort_col = getattr(Fulfillment, sort_by, Fulfillment.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(sort_col.asc())
        else:
            stmt = stmt.order_by(sort_col.desc())
        total = int(db.scalar(count_stmt) or 0)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        return list(db.scalars(stmt)), total

    @staticmethod
    def create_row(db: Session, payload: FulfillmentCreate) -> Fulfillment:
        obj = Fulfillment(**payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def update_row(db: Session, row_id: int, payload: FulfillmentUpdate) -> Fulfillment | None:
        obj = db.get(Fulfillment, row_id)
        if not obj:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

