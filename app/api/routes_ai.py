"""AI 路由。"""

from fastapi import APIRouter
from app.schemas.ai import ChatRequest
from app.schemas.common import ApiResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/chat", response_model=ApiResponse)
def chat(payload: ChatRequest) -> ApiResponse:
    """调用真实大模型进行问答。"""
    result = AIService.ask(payload.question)
    return ApiResponse(data=result)

