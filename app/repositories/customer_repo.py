"""客户数据访问层。"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.entities import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerRepository:
    """
    客户仓储类（Repository Pattern）。
    将数据访问细节封装，业务层无需关心 ORM 细节。
    """

    @staticmethod
    def list_customers(
        db: Session,
        keyword: str | None = None,
        grade: str | None = None,
        owner: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "id",
        sort_order: str = "desc",
    ) -> tuple[list[Customer], int]:
        stmt = select(Customer)
        count_stmt = select(func.count()).select_from(Customer)
        if keyword:
            stmt = stmt.where(Customer.customer_name.contains(keyword))
            count_stmt = count_stmt.where(Customer.customer_name.contains(keyword))
        if grade:
            stmt = stmt.where(Customer.grade == grade)
            count_stmt = count_stmt.where(Customer.grade == grade)
        if owner:
            stmt = stmt.where(Customer.owner == owner)
            count_stmt = count_stmt.where(Customer.owner == owner)

        sort_col = getattr(Customer, sort_by, Customer.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(sort_col.asc())
        else:
            stmt = stmt.order_by(sort_col.desc())

        total = int(db.scalar(count_stmt) or 0)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        return list(db.scalars(stmt)), total

    @staticmethod
    def create_customer(db: Session, payload: CustomerCreate) -> Customer:
        obj = Customer(**payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def update_customer(db: Session, customer_id: int, payload: CustomerUpdate) -> Customer | None:
        obj = db.get(Customer, customer_id)
        if not obj:
            return None
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

