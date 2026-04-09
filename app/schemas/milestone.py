"""履约里程碑模型。"""

from datetime import datetime
from pydantic import BaseModel


class MilestoneBase(BaseModel):
    fulfill_id: int
    milestone_name: str
    due_date: str = ""
    status: str = "未开始"
    owner: str = "系统"
    warning_level: str = "正常"
    notes: str = ""


class MilestoneCreate(MilestoneBase):
    """创建里程碑请求。"""


class MilestoneUpdate(BaseModel):
    milestone_name: str | None = None
    due_date: str | None = None
    status: str | None = None
    owner: str | None = None
    warning_level: str | None = None
    notes: str | None = None


class MilestoneOut(MilestoneBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

