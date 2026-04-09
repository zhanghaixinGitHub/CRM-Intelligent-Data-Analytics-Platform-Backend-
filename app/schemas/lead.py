"""线索模型。"""

from datetime import datetime
from pydantic import BaseModel


class LeadBase(BaseModel):
    lead_code: str
    lead_name: str
    customer_name: str = ""
    source: str = "展会"
    region: str = "中国区"
    product_direction: str = "AR眼镜"
    priority: str = "中"
    status: str = "线索验证"
    owner: str = "系统"
    contact: str = ""
    phone: str = ""
    converted_opportunity_code: str = ""
    notes: str = ""


class LeadCreate(LeadBase):
    """创建线索请求。"""


class LeadUpdate(BaseModel):
    lead_name: str | None = None
    customer_name: str | None = None
    source: str | None = None
    region: str | None = None
    product_direction: str | None = None
    priority: str | None = None
    status: str | None = None
    owner: str | None = None
    contact: str | None = None
    phone: str | None = None
    converted_opportunity_code: str | None = None
    notes: str | None = None


class LeadOut(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

