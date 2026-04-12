"""AI 高级能力路由。"""

from fastapi import APIRouter

from app.schemas.ai_advanced import DecisionWorkflowRequest, PromptLabRequest
from app.schemas.common import ApiResponse
from app.services.ai_advanced_service import AIAdvancedService

router = APIRouter(prefix="/api/ai-advanced", tags=["ai-advanced"])


@router.post("/prompt-lab", response_model=ApiResponse)
def prompt_lab(payload: PromptLabRequest) -> ApiResponse:
    """
    提示词工程实验室接口（中等复杂度页面）。
    该接口用于承载 Prompt 模板、Few-shot、输出约束等配置。
    """
    data = AIAdvancedService.run_prompt_lab(
        template_type=payload.template_type,
        system_prompt=payload.system_prompt,
        business_context=payload.business_context,
        user_question=payload.user_question,
        few_shot_examples=payload.few_shot_examples,
        safety_rules=payload.safety_rules,
        output_mode=payload.output_mode,
        enable_refine=payload.enable_refine,
    )
    return ApiResponse(data=data)


@router.post("/decision-workflow", response_model=ApiResponse)
def decision_workflow(payload: DecisionWorkflowRequest) -> ApiResponse:
    """
    多智能体协同决策接口（较高复杂度页面）。
    该接口按固定工作流执行：解析 -> 检索 -> 多代理 -> 仲裁 -> 看板。
    """
    data = AIAdvancedService.run_decision_workflow(
        goal=payload.goal,
        opportunity_context=payload.opportunity_context,
        knowledge_base=payload.knowledge_base,
        max_agents=payload.max_agents,
        need_kanban=payload.need_kanban,
    )
    return ApiResponse(data=data)

