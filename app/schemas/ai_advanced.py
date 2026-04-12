"""AI 高级场景请求/响应模型。"""

from pydantic import BaseModel, Field


class PromptLabRequest(BaseModel):
    """
    提示词工程实验室请求模型。
    该模型对应前端“中等复杂度页面”，用于承载完整提示词配置。
    """

    template_type: str = Field(default="sales_summary", description="任务模板类型")
    system_prompt: str = Field(..., description="系统角色提示词")
    business_context: str = Field(..., description="业务上下文")
    user_question: str = Field(..., description="用户问题")
    few_shot_examples: str = Field(default="", description="少样本示例")
    safety_rules: list[str] = Field(default_factory=list, description="安全与边界约束")
    output_mode: str = Field(default="json", description="输出模式：json/markdown")
    enable_refine: bool = Field(default=True, description="是否开启自我反思重写")


class DecisionWorkflowRequest(BaseModel):
    """
    多智能体协同决策请求模型。
    该模型对应前端“较高复杂度页面”，用于工作流编排。
    """

    goal: str = Field(..., description="决策目标")
    opportunity_context: str = Field(..., description="商机上下文")
    knowledge_base: str = Field(default="", description="知识库文本")
    max_agents: int = Field(default=3, ge=1, le=3, description="最大代理数")
    need_kanban: bool = Field(default=True, description="是否返回执行看板")

