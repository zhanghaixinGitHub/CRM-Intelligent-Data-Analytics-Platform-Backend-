"""看板模型。"""

from pydantic import BaseModel


class MetricCard(BaseModel):
    title: str
    value: str
    extra: str = ""
    color: str = "#1f6bff"


class DashboardData(BaseModel):
    cards: list[MetricCard]
    funnel: list[dict]
    bu_trend: list[dict]
    stage_progress: list[dict]

