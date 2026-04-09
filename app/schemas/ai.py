"""AI 问答模型。"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sql_hint: str
    chart_suggestion: str

