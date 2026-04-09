"""AI 对话服务。"""

from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.core.logger import CRMLogger


class AIService:
    """
    AI 服务类（Facade Pattern）。
    对外统一暴露问答能力，隐藏底层大模型调用细节。
    """

    _llm = ChatOpenAI(
        model_name=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        temperature=0.2,
    )

    @classmethod
    def ask(cls, question: str) -> dict:
        """
        对话式数据分析问答。
        返回回答 + SQL提示 + 图表建议，方便前端直接渲染。
        """
        CRMLogger.info("AIService.ask", f"收到问题：{question}")
        prompt = f"""
你是CRM智能数据分析助手，请用中文回答，要求简洁可执行。
用户问题：{question}

请严格按下面格式回复：
回答：
<你的分析结论>
SQL建议：
<可执行的SQLite SQL或伪SQL>
图表建议：
<推荐的图表类型和原因>
"""
        response = cls._llm.invoke(prompt)
        text = response.content if isinstance(response.content, str) else str(response.content)

        # 这里做一个轻量解析，避免依赖额外解析库。
        answer = text
        sql_hint = "SELECT * FROM opportunities LIMIT 10;"
        chart_suggestion = "柱状图：展示各阶段金额对比"

        if "SQL建议：" in text:
            parts = text.split("SQL建议：")
            answer = parts[0].replace("回答：", "").strip()
            tail = parts[1]
            if "图表建议：" in tail:
                sql_hint = tail.split("图表建议：")[0].strip()
                chart_suggestion = tail.split("图表建议：")[1].strip()
            else:
                sql_hint = tail.strip()

        return {
            "answer": answer,
            "sql_hint": sql_hint,
            "chart_suggestion": chart_suggestion,
        }

