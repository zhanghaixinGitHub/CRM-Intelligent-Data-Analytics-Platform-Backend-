"""商机模型。"""

from datetime import datetime
from pydantic import BaseModel


class OpportunityBase(BaseModel):
    opp_code: str
    opp_name: str
    customer_name: str
    product_form: str = "AR眼镜"
    product_line: str = "XR"
    cooperation_mode: str = "NRE"
    stage: str = "stage3"
    amount: float = 0.0
    win_rate: float = 0.0
    next_action: str = ""
    owner: str = "系统"


class OpportunityCreate(OpportunityBase):
    """创建商机请求。"""


class OpportunityUpdate(BaseModel):
    opp_name: str | None = None
    stage: str | None = None
    amount: float | None = None
    win_rate: float | None = None
    next_action: str | None = None
    owner: str | None = None


class OpportunityOut(OpportunityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

