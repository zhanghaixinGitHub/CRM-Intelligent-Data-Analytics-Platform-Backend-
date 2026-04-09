"""履约模型。"""

from datetime import datetime
from pydantic import BaseModel


class FulfillmentBase(BaseModel):
    fulfill_code: str
    project_name: str
    customer_name: str
    stage: str = "赢单阶段"
    progress: str = "0%"
    amount: float = 0.0
    delivery_date: str = ""
    owner: str = "系统"
    risk_level: str = "低"
    notes: str = ""


class FulfillmentCreate(FulfillmentBase):
    """创建履约请求。"""


class FulfillmentUpdate(BaseModel):
    project_name: str | None = None
    customer_name: str | None = None
    stage: str | None = None
    progress: str | None = None
    amount: float | None = None
    delivery_date: str | None = None
    owner: str | None = None
    risk_level: str | None = None
    notes: str | None = None


class FulfillmentOut(FulfillmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

