"""系统配置模块。"""

from pathlib import Path
from pydantic import BaseModel


class Settings(BaseModel):
    """统一管理系统配置，便于后续扩展多环境。"""

    app_name: str = "CRM智能数据分析平台"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    debug: bool = True

    sqlite_path: Path = Path("crm_ai.db")

    # 你提供的大模型配置（按你的要求直接内置）
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = "https://api.openai-proxy.org/v1"
    llm_api_key: str = "sk-rbfyYt7GrXr9H3teqm56li0Jz8MsH0eRNhZs4MKZDH6inxKg"
    # Prompt 版本号：用于可观测性和回溯（生产中建议跟随发布版本维护）
    llm_prompt_version: str = "v1.1.0"
    # 场景化模型路由：正式项目常按场景做模型分流（成本/速度/质量平衡）
    # 说明：
    # - general：普通问答或默认场景
    # - prompt_lab：提示词实验场景
    # - agent_analysis：多代理分析场景
    # - arbiter：仲裁汇总场景（可用更强模型）
    llm_model_router: dict[str, str] = {
        "general": "gpt-4o-mini",
        "prompt_lab": "gpt-4o-mini",
        "agent_analysis": "gpt-4o-mini",
        "arbiter": "gpt-4o-mini",
    }


settings = Settings()

