"""AI 高级服务：提示词实验室 + 多智能体协同。"""

import re
import time
from typing import Callable

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.core.config import settings
from app.core.logger import CRMLogger


class AIAdvancedService:
    """
    AI 高级服务（Facade + Strategy + Template Method）。

    - Facade：对外统一暴露高级 AI 能力，隐藏底层编排细节。
    - Strategy：通过模板策略生成不同任务提示词。
    - Template Method：固定多智能体工作流主骨架，便于后续扩展步骤。
    """

    _llm_cache: dict[str, ChatOpenAI] = {}

    _template_strategies: dict[str, Callable[[str, str], str]] = {
        "sales_summary": lambda business_context, user_question: f"""
[任务]
请以 CRM 销售经理视角，先总结结论，再给执行建议。
[业务上下文]
{business_context}
[用户问题]
{user_question}
""".strip(),
        "risk_check": lambda business_context, user_question: f"""
[任务]
请以 风险审查官 视角，识别关键风险并给缓解措施。
[业务上下文]
{business_context}
[用户问题]
{user_question}
""".strip(),
        "action_plan": lambda business_context, user_question: f"""
[任务]
请以 一线销售教练 视角，输出未来7天行动清单（按优先级）。
[业务上下文]
{business_context}
[用户问题]
{user_question}
""".strip(),
    }

    @classmethod
    def run_prompt_lab(
        cls,
        template_type: str,
        system_prompt: str,
        business_context: str,
        user_question: str,
        few_shot_examples: str,
        safety_rules: list[str],
        output_mode: str,
        enable_refine: bool,
    ) -> dict:
        """
        运行提示词工程实验。

        关键配置说明（学习重点）：
        1) system_prompt：控制角色和边界，避免“跑偏”；
        2) strategy template：控制任务目标，让输出稳定；
        3) few_shot：通过样例约束风格；
        4) safety_rules：控制合规与风控；
        5) output_mode：保证结果可解析（适配前端展示/存储）。
        """
        started = time.time()
        CRMLogger.info("AIAdvancedService.run_prompt_lab", f"收到实验请求，模板={template_type}")
        strategy = cls._template_strategies.get(template_type, cls._template_strategies["sales_summary"])
        task_prompt = strategy(business_context, user_question)
        output_rule = (
            "请严格输出JSON，字段必须为：answer, sql_hint, chart_suggestion。"
            if output_mode == "json"
            else "请按Markdown结构输出：回答 / SQL建议 / 图表建议。"
        )
        refine_rule = (
            """
[自我反思]
请先给初稿，再按“结论清晰度、可执行性、风险覆盖”重写一轮最终答案。
""".strip()
            if enable_refine
            else ""
        )

        final_prompt = f"""
[System]
{system_prompt}

{task_prompt}

[Few-Shot]
{few_shot_examples}

[Safety Rules]
{chr(10).join([f"{idx + 1}. {rule}" for idx, rule in enumerate(safety_rules)])}

[Output Rules]
{output_rule}

{refine_rule}
""".strip()

        answer_text, sql_hint, chart_suggestion, trace = cls._ask_and_parse(final_prompt, scene="prompt_lab")
        quality = cls._score_result(answer_text=answer_text, sql_hint=sql_hint, chart_suggestion=chart_suggestion)
        return {
            "prompt_preview": final_prompt,
            "answer": answer_text,
            "sql_hint": sql_hint,
            "chart_suggestion": chart_suggestion,
            "quality_score": quality["score"],
            "quality_detail": quality["detail"],
            "trace": {
                "scene": "prompt_lab",
                "model_name": trace["model_name"],
                "prompt_version": settings.llm_prompt_version,
                "prompt_chars": len(final_prompt),
                "token_estimate": len(final_prompt) // 4 + 1,
                "retry_count": trace["retry_count"],
                "model_latency_ms": trace["latency_ms"],
                "duration_ms": int((time.time() - started) * 1000),
            },
        }

    @classmethod
    def run_decision_workflow(
        cls,
        goal: str,
        opportunity_context: str,
        knowledge_base: str,
        max_agents: int,
        need_kanban: bool,
    ) -> dict:
        """
        多智能体协同决策模板方法：
        步骤固定为：解析 -> 检索 -> 代理分析 -> 仲裁 -> 生成执行看板。
        """
        started = time.time()
        logs: list[str] = []
        metrics = {"token_estimate": 0, "agent_calls": 0, "duration_ms": 0}
        step_timings: dict[str, int] = {}
        retry_count_total = 0
        scene_models: dict[str, str] = {}

        def log_info(message: str) -> None:
            logs.append(f"AIAdvancedService.run_decision_workflow >>> {message}")
            CRMLogger.info("AIAdvancedService.run_decision_workflow", message)

        stage_start = time.time()
        log_info("步骤1：解析业务上下文")
        context = opportunity_context.strip()
        step_timings["parse_context_ms"] = int((time.time() - stage_start) * 1000)

        stage_start = time.time()
        log_info("步骤2：执行RAG-Lite检索")
        retrieved = cls._retrieve_context(goal=goal, kb_text=knowledge_base)
        log_info(f"检索到 {len(retrieved)} 条知识片段")
        step_timings["retrieve_context_ms"] = int((time.time() - stage_start) * 1000)

        stage_start = time.time()
        log_info("步骤3：多代理分析")
        ordered_agents = ["sales_agent", "risk_agent", "delivery_agent"]
        selected_agents = ordered_agents[: max(1, min(max_agents, 3))]
        outputs = []
        for agent in selected_agents:
            prompt = cls._build_agent_prompt(agent=agent, context=context, goal=goal, retrieved=retrieved)
            metrics["token_estimate"] += len(prompt) // 4 + 1
            metrics["agent_calls"] += 1
            out = cls._call_agent(agent=agent, prompt=prompt)
            outputs.append(out)
            retry_count_total += int(out["trace"]["retry_count"])
            scene_models[f"agent_{agent}"] = out["trace"]["model_name"]
        step_timings["agent_analysis_ms"] = int((time.time() - stage_start) * 1000)

        stage_start = time.time()
        log_info("步骤4：仲裁代理合并结论")
        arbiter_prompt = cls._build_arbiter_prompt(goal=goal, context=context, outputs=outputs)
        metrics["token_estimate"] += len(arbiter_prompt) // 4 + 1
        metrics["agent_calls"] += 1
        final_answer, final_sql, final_chart, arbiter_trace = cls._ask_and_parse(arbiter_prompt, scene="arbiter")
        retry_count_total += int(arbiter_trace["retry_count"])
        scene_models["arbiter"] = arbiter_trace["model_name"]
        step_timings["arbiter_ms"] = int((time.time() - stage_start) * 1000)

        stage_start = time.time()
        confidence = cls._parse_confidence(final_answer)
        execution_board = cls._build_execution_board(final_answer) if need_kanban else []
        step_timings["build_kanban_ms"] = int((time.time() - stage_start) * 1000)

        metrics["duration_ms"] = int((time.time() - started) * 1000)
        log_info("步骤5：流程执行完成")

        return {
            "final_decision": final_answer,
            "decision_reason": "来自销售、风控、交付代理的交叉结论，降低单点判断偏差。",
            "sql_hint": final_sql,
            "chart_hint": final_chart,
            "confidence": confidence,
            "execution_board": execution_board,
            "retrieved_context": retrieved,
            "agent_outputs": outputs,
            "logs": logs,
            "metrics": metrics,
            "observability": {
                "prompt_version": settings.llm_prompt_version,
                "scene_models": scene_models,
                "retry_count_total": retry_count_total,
                "step_timings": step_timings,
            },
        }

    @classmethod
    def _ask_and_parse(cls, prompt: str, scene: str) -> tuple[str, str, str, dict]:
        """
        统一调用模型并做轻量解析。
        解析规则与现有 AIService 保持一致，便于前后端复用。
        """
        text, trace = cls._invoke_with_retry(prompt=prompt, scene=scene)
        answer = text
        sql_hint = "SELECT * FROM opportunities LIMIT 10;"
        chart_suggestion = "柱状图：按阶段展示金额对比"
        if "SQL建议：" in text:
            parts = text.split("SQL建议：")
            answer = parts[0].replace("回答：", "").strip()
            tail = parts[1]
            if "图表建议：" in tail:
                sql_hint = tail.split("图表建议：")[0].strip()
                chart_suggestion = tail.split("图表建议：")[1].strip()
            else:
                sql_hint = tail.strip()
        return answer, sql_hint, chart_suggestion, trace

    @classmethod
    def _score_result(cls, answer_text: str, sql_hint: str, chart_suggestion: str) -> dict:
        """按可用性做基础质量评分。"""
        score = 0
        detail: list[str] = []
        if answer_text.strip():
            score += 35
            detail.append("1) 结论输出：通过(+35)")
        else:
            detail.append("1) 结论输出：缺失(+0)")

        if sql_hint.strip():
            score += 30
            detail.append("2) SQL建议：存在(+30)")
        else:
            detail.append("2) SQL建议：缺失(+0)")

        if chart_suggestion.strip():
            score += 25
            detail.append("3) 图表建议：存在(+25)")
        else:
            detail.append("3) 图表建议：缺失(+0)")

        if not re.search(r"编造|胡乱|随便", answer_text, re.IGNORECASE):
            score += 10
            detail.append("4) 安全边界：通过(+10)")
        else:
            detail.append("4) 安全边界：疑似违反(+0)")
        return {"score": score, "detail": "\n".join(detail)}

    @classmethod
    def _retrieve_context(cls, goal: str, kb_text: str) -> list[str]:
        """
        RAG-Lite：关键词匹配检索。
        正式项目可替换为向量检索（Embedding + Vector DB），接口层无需改动。
        """
        words = [item for item in re.split(r"[\s,，。；;]+", goal) if item]
        lines = [item.strip() for item in kb_text.split("\n") if item.strip()]
        scored = []
        for line in lines:
            hit = sum(1 for word in words if word in line)
            scored.append((line, hit))
        top_k = sorted(scored, key=lambda item: item[1], reverse=True)[:3]
        return [item[0] for item in top_k]

    @classmethod
    def _build_agent_prompt(cls, agent: str, context: str, goal: str, retrieved: list[str]) -> str:
        role_map = {
            "sales_agent": "你是销售策略顾问，负责判断成交概率与行动优先级。",
            "risk_agent": "你是风险控制顾问，负责识别推进风险与缓解措施。",
            "delivery_agent": "你是交付经理顾问，负责评估交付可行性和资源压力。",
        }
        role = role_map.get(agent, role_map["sales_agent"])
        return f"""
[角色]
{role}

[目标]
{goal}

[上下文]
{context}

[检索知识]
{chr(10).join([f"- {line}" for line in retrieved])}

[输出要求]
请给出结论、依据、动作建议，并补充SQL建议和图表建议。
""".strip()

    @classmethod
    def _call_agent(cls, agent: str, prompt: str) -> dict:
        CRMLogger.info("AIAdvancedService._call_agent", f"开始调用代理：{agent}")
        answer, sql_hint, chart_suggestion, trace = cls._ask_and_parse(prompt, scene="agent_analysis")
        CRMLogger.info("AIAdvancedService._call_agent", f"代理调用完成：{agent}")
        return {
            "agent": agent,
            "answer": answer,
            "sql_hint": sql_hint,
            "chart_suggestion": chart_suggestion,
            "trace": trace,
        }

    @classmethod
    def _build_arbiter_prompt(cls, goal: str, context: str, outputs: list[dict]) -> str:
        return f"""
[角色]
你是仲裁代理，负责统一多个代理观点并给最终建议。

[目标]
{goal}

[原始上下文]
{context}

[代理输出]
{chr(10).join([f"- 代理={item['agent']} 结论={item['answer']}" for item in outputs])}

[输出要求]
请输出：最终建议、关键依据、SQL建议、图表建议、置信度（0-100）。
""".strip()

    @classmethod
    def _parse_confidence(cls, answer_text: str) -> int:
        matched = re.search(r"(\d{1,3})", answer_text)
        if not matched:
            return 75
        value = int(matched.group(1))
        if value < 0:
            return 0
        if value > 100:
            return 100
        return value

    @classmethod
    def _build_execution_board(cls, answer_text: str) -> list[dict]:
        """根据仲裁结果返回可执行看板。"""
        board = [
            {
                "owner": "销售经理",
                "task": "组织客户决策链复盘，确认预算审批阻塞点并安排复访。",
                "deadline": "T+1天",
                "risk": "关键决策人未参会导致推进延迟",
            },
            {
                "owner": "交付经理",
                "task": "输出分阶段上线计划与SLA承诺，提升客户交付信心。",
                "deadline": "T+2天",
                "risk": "资源排期冲突影响承诺可兑现性",
            },
            {
                "owner": "风控专员",
                "task": "审查分期付款条款并给回款风险等级建议。",
                "deadline": "T+2天",
                "risk": "条款模糊导致回款争议",
            },
        ]
        if len(answer_text) > 120:
            board[0]["task"] = "结合仲裁结论输出客户异议闭环清单，并安排联合拜访。"
        return board

    @classmethod
    def _select_model_for_scene(cls, scene: str) -> str:
        """
        按业务场景选择模型。
        正式项目常见做法：低成本模型跑草稿，高质量模型做仲裁/最终输出。
        """
        return settings.llm_model_router.get(scene, settings.llm_model_router.get("general", settings.llm_model))

    @classmethod
    def _get_llm(cls, scene: str) -> ChatOpenAI:
        model_name = cls._select_model_for_scene(scene)
        cache_key = f"{scene}:{model_name}"
        if cache_key not in cls._llm_cache:
            cls._llm_cache[cache_key] = ChatOpenAI(
                model=model_name,
                base_url=settings.llm_base_url,
                api_key=SecretStr(settings.llm_api_key),
                temperature=0.2,
            )
            CRMLogger.info("AIAdvancedService._get_llm", f"初始化模型实例，scene={scene}, model={model_name}")
        return cls._llm_cache[cache_key]

    @classmethod
    def _invoke_with_retry(cls, prompt: str, scene: str, max_retries: int = 1) -> tuple[str, dict]:
        """
        模型调用重试机制（简化版）：
        - 首次调用失败后最多重试1次，减少瞬时网络波动影响。
        - 返回 trace 供前端可观测面板展示。
        """
        llm = cls._get_llm(scene=scene)
        model_name = cls._select_model_for_scene(scene)
        last_error = ""
        for attempt in range(max_retries + 1):
            start = time.time()
            try:
                response = llm.invoke(prompt)
                text = response.content if isinstance(response.content, str) else str(response.content)
                latency_ms = int((time.time() - start) * 1000)
                trace = {"scene": scene, "model_name": model_name, "retry_count": attempt, "latency_ms": latency_ms}
                return text, trace
            except Exception as exc:
                last_error = str(exc)
                CRMLogger.error("AIAdvancedService._invoke_with_retry", f"调用失败，scene={scene}, attempt={attempt}, err={last_error}")
                if attempt >= max_retries:
                    raise
        raise RuntimeError(f"模型调用失败：{last_error}")

