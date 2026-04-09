"""商机服务层。"""

from sqlalchemy.orm import Session
from app.core.logger import CRMLogger
from app.models.entities import Opportunity
from app.schemas.opportunity_stage import OpportunityAdvanceRequest


class OpportunityService:
    """
    商机服务类（Service Pattern）。
    负责商机阶段推进与规则校验，确保流程符合业务规范。
    """

    STAGE_ORDER = ["stage1", "stage2", "stage3", "stage4", "stage5", "stage6"]

    @classmethod
    def advance_stage(cls, db: Session, opp_id: int, payload: OpportunityAdvanceRequest) -> dict | None:
        opp = db.get(Opportunity, opp_id)
        if not opp:
            return None

        current_stage = opp.stage
        target_stage = payload.target_stage
        if target_stage not in cls.STAGE_ORDER:
            raise ValueError("目标阶段非法")

        if cls.STAGE_ORDER.index(target_stage) < cls.STAGE_ORDER.index(current_stage):
            raise ValueError("不允许阶段倒退，请走回退审批流程")

        # 阶段校验规则：更贴近真实流程的门禁控制
        if target_stage == "stage4" and not payload.proposal_doc_uploaded:
            raise ValueError("推进到stage4前，必须上传提案资料")
        if target_stage == "stage5" and not payload.review_passed:
            raise ValueError("推进到stage5前，必须通过提案评审")

        opp.stage = target_stage
        if target_stage == "stage6":
            opp.win_rate = max(opp.win_rate, 0.85)
            opp.next_action = "进入履约移交流程"
        db.commit()
        db.refresh(opp)

        CRMLogger.info("OpportunityService.advance_stage", f"商机推进成功 opp_id={opp_id}, {current_stage}->{target_stage}")
        return {
            "opportunity_id": opp.id,
            "opp_code": opp.opp_code,
            "old_stage": current_stage,
            "new_stage": opp.stage,
            "message": "商机阶段推进成功",
        }

