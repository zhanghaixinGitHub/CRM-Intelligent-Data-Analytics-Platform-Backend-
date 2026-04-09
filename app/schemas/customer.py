"""客户模型。"""

from datetime import datetime
from pydantic import BaseModel


class CustomerBase(BaseModel):
    customer_name: str
    customer_code: str
    grade: str = "B"
    region: str = "华东"
    industry: str = "消费电子"
    owner: str = "系统"
    tags: str = ""
    last_follow_up: str = ""


class CustomerCreate(CustomerBase):
    """创建客户请求。"""


class CustomerUpdate(BaseModel):
    customer_name: str | None = None
    grade: str | None = None
    region: str | None = None
    industry: str | None = None
    owner: str | None = None
    tags: str | None = None
    last_follow_up: str | None = None


class CustomerOut(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

