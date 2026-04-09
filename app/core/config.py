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


settings = Settings()

