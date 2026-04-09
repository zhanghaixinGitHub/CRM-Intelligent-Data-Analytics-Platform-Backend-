"""线索服务层。"""

from datetime import datetime
from sqlalchemy.orm import Session
from app.core.logger import CRMLogger
from app.repositories.fulfillment_repo import FulfillmentRepository
from app.repositories.lead_repo import LeadRepository
from app.repositories.milestone_repo import MilestoneRepository
from app.repositories.opportunity_repo import OpportunityRepository
from app.schemas.fulfillment import FulfillmentCreate
from app.schemas.lead import LeadUpdate
from app.schemas.milestone import MilestoneCreate
from app.schemas.opportunity import OpportunityCreate


class LeadService:
    """
    线索服务类（Service Pattern）。
    这里封装线索转商机的跨聚合业务逻辑，避免路由层写复杂流程。
    """

    @staticmethod
    def convert_to_opportunity(db: Session, lead_id: int, owner: str = "系统") -> dict | None:
        lead = LeadRepository.get_by_id(db, lead_id)
        if not lead:
            return None
        if lead.status not in ("立项资料", "立项评审", "线索验证"):
            raise ValueError("当前线索状态不允许转商机")
        if lead.converted_opportunity_code:
            raise ValueError("该线索已转过商机，请勿重复转化")

        CRMLogger.info("LeadService.convert_to_opportunity", f"开始转化线索 lead_id={lead_id}")
        opp_code = f"LTCZ{datetime.now().strftime('%m%d%H%M')}{str(lead_id).zfill(2)}"
        opp_payload = OpportunityCreate(
            opp_code=opp_code,
            opp_name=f"{lead.lead_name}-转化商机",
            customer_name=lead.customer_name or lead.lead_name,
            product_form=lead.product_direction,
            product_line="XR",
            cooperation_mode="NRE",
            stage="stage3",
            amount=80_000_000,
            win_rate=0.50,
            next_action="完成提案准备材料",
            owner=owner,
        )
        opp = OpportunityRepository.create_opportunity(db, opp_payload)
        LeadRepository.update_lead(
            db,
            lead_id,
            LeadUpdate(status="已转商机", converted_opportunity_code=opp.opp_code, owner=owner),
        )

        # 真实项目中，商机转化后通常会提前初始化履约主表与关键里程碑，
        # 这样销售与交付团队可以无缝衔接，避免“赢单后再手工补单据”的断档。
        fulfill = FulfillmentRepository.create_row(
            db,
            FulfillmentCreate(
                fulfill_code=f"FUL{opp.opp_code[-10:]}",
                project_name=f"{opp.opp_name}-履约初始化",
                customer_name=opp.customer_name,
                stage="赢单阶段",
                progress="10%",
                amount=opp.amount,
                delivery_date="",
                owner=owner,
                risk_level="中",
                notes="由线索转商机自动生成履约主记录",
            ),
        )
        MilestoneRepository.create(
            db,
            MilestoneCreate(
                fulfill_id=fulfill.id,
                milestone_name="商务移交会",
                due_date=datetime.now().strftime("%Y-%m-%d"),
                status="未开始",
                owner=owner,
                warning_level="正常",
                notes="自动生成：确保销售与交付完成移交",
            ),
        )
        MilestoneRepository.create(
            db,
            MilestoneCreate(
                fulfill_id=fulfill.id,
                milestone_name="技术方案冻结",
                due_date="",
                status="未开始",
                owner=owner,
                warning_level="正常",
                notes="自动生成：项目进入执行前需完成方案冻结",
            ),
        )

        return {
            "lead_id": lead_id,
            "opportunity_id": opp.id,
            "opportunity_code": opp.opp_code,
            "fulfillment_id": fulfill.id,
            "message": "线索已成功转为商机",
        }

