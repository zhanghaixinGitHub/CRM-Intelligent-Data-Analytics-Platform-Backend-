"""初始化测试数据。"""

from sqlalchemy.orm import Session
from app.models.entities import Customer, Fulfillment, FulfillmentMilestone, Lead, Opportunity


def init_seed_data(db: Session) -> None:
    """首次启动写入示例数据，保证页面可直接展示。"""
    # 为了让页面“看起来像真实业务系统”，这里一次性准备更丰富的演示数据。
    # 这些数据覆盖线索、客户、商机、履约四条核心链路。
    if db.query(Customer).count() == 0:
        customers = [
            Customer(customer_name="理光金服", customer_code="CUS2026001", grade="A", region="华东", industry="AR眼镜", owner="张强", tags="战略客户,高潜"),
            Customer(customer_name="ASUS", customer_code="CUS2026002", grade="A", region="华南", industry="AR眼镜", owner="刘海", tags="重点客户"),
            Customer(customer_name="Uniquest", customer_code="CUS2026003", grade="B", region="华东", industry="5G SoM", owner="李健", tags="成长型"),
            Customer(customer_name="Logitech", customer_code="CUS2026004", grade="B", region="华北", industry="Video", owner="王磊", tags="稳定客户"),
            Customer(customer_name="Qualcomm", customer_code="CUS2026005", grade="A", region="海外", industry="Others", owner="赵云", tags="战略客户"),
            Customer(customer_name="Arvicom", customer_code="CUS2026006", grade="B", region="华北", industry="XR", owner="李俊", tags="持续跟进"),
            Customer(customer_name="Pixelplus", customer_code="CUS2026007", grade="C", region="华东", industry="Camera", owner="周宁", tags="培育客户"),
        ]
        db.add_all(customers)

    if db.query(Opportunity).count() == 0:
        opportunities = [
            Opportunity(opp_code="LTCY202603002", opp_name="智驭全联-AR1 Plus", customer_name="理光金服", product_form="AR眼镜", product_line="XR", cooperation_mode="COB", stage="stage6", amount=350_000_000, win_rate=0.87, next_action="推进量产排期确认", owner="张强"),
            Opportunity(opp_code="LTCY202510001", opp_name="ASUS-AR眼镜", customer_name="ASUS", product_form="AR眼镜", product_line="XR", cooperation_mode="NRE", stage="stage5", amount=220_000_000, win_rate=0.72, next_action="完成样机验收", owner="刘海"),
            Opportunity(opp_code="LTCY202603008", opp_name="行者无疆-BES 2700", customer_name="行者无疆", product_form="AR/XR眼镜一体机", product_line="XR", cooperation_mode="Whole Device", stage="stage4", amount=160_000_000, win_rate=0.63, next_action="商务条款谈判", owner="周宁"),
            Opportunity(opp_code="LTCR202603001", opp_name="Uniquest-T62-5G", customer_name="Uniquest", product_form="5G SoM", product_line="Cellular SoM", cooperation_mode="SOM", stage="stage3", amount=110_000_000, win_rate=0.55, next_action="确认试产方案", owner="李健"),
            Opportunity(opp_code="LTCW202603012", opp_name="Logitech-8750", customer_name="Logitech", product_form="视频会议", product_line="Video", cooperation_mode="NRE", stage="stage2", amount=75_000_000, win_rate=0.42, next_action="补充成本测算", owner="王磊"),
            Opportunity(opp_code="LTCU202603005", opp_name="Arvicom-XR2-AR", customer_name="Arvicom", product_form="AR眼镜", product_line="XR", cooperation_mode="SOM", stage="stage4", amount=98_000_000, win_rate=0.66, next_action="推进提案评审", owner="李俊"),
            Opportunity(opp_code="LTCW202603004", opp_name="亚洲光学-AR1 Gen2", customer_name="亚洲光学", product_form="AR眼镜", product_line="XR", cooperation_mode="COB", stage="stage3", amount=88_000_000, win_rate=0.58, next_action="组织客户定标会", owner="周宁"),
        ]
        db.add_all(opportunities)

    if db.query(Lead).count() == 0:
        leads = [
            Lead(lead_code="LEAD2026001", lead_name="理光金服AR升级需求", customer_name="理光金服", source="展会", region="中国区", product_direction="AR眼镜", priority="高", status="线索验证", owner="张强", contact="李总", phone="13800001001", converted_opportunity_code="", notes="客户希望Q3完成样机验证"),
            Lead(lead_code="LEAD2026002", lead_name="ASUS下一代XR项目", customer_name="ASUS", source="客户转介绍", region="中国区", product_direction="XR", priority="高", status="立项资料", owner="刘海", contact="Ming", phone="13800001002", notes="已进入立项资料收集"),
            Lead(lead_code="LEAD2026003", lead_name="Uniquest 5G模组需求", customer_name="Uniquest", source="渠道", region="华东", product_direction="5G SoM", priority="中", status="立项评审", owner="李健", contact="Andy", phone="13800001003", notes="本周完成立项评审"),
            Lead(lead_code="LEAD2026004", lead_name="Pixelplus Camera SoM", customer_name="Pixelplus", source="线上线索", region="华东", product_direction="Camera", priority="中", status="线索录入", owner="周宁", contact="Park", phone="13800001004", notes="等待技术团队初评"),
            Lead(lead_code="LEAD2026005", lead_name="Logitech 视频会议升级", customer_name="Logitech", source="老客户复购", region="华北", product_direction="Video", priority="低", status="线索验证", owner="王磊", contact="Alan", phone="13800001005", converted_opportunity_code="", notes="预计下月进入立项"),
        ]
        db.add_all(leads)

    if db.query(Fulfillment).count() == 0:
        fulfillments = [
            Fulfillment(fulfill_code="FUL2026001", project_name="理光金服AR1量产项目", customer_name="理光金服", stage="赢单阶段", progress="95%", amount=320_000_000, delivery_date="2026-06-30", owner="张强", risk_level="低", notes="合同已签，等待PO释放"),
            Fulfillment(fulfill_code="FUL2026002", project_name="ASUS XR样机交付", customer_name="ASUS", stage="开发阶段", progress="62%", amount=180_000_000, delivery_date="2026-08-15", owner="刘海", risk_level="中", notes="驱动适配存在排期风险"),
            Fulfillment(fulfill_code="FUL2026003", project_name="Uniquest T62试产", customer_name="Uniquest", stage="开发阶段", progress="48%", amount=110_000_000, delivery_date="2026-09-01", owner="李健", risk_level="中", notes="需追加测试资源"),
            Fulfillment(fulfill_code="FUL2026004", project_name="Logitech 视频会议模组", customer_name="Logitech", stage="量产阶段", progress="76%", amount=96_000_000, delivery_date="2026-07-20", owner="王磊", risk_level="低", notes="量产节奏稳定"),
            Fulfillment(fulfill_code="FUL2026005", project_name="Arvicom XR2 出货", customer_name="Arvicom", stage="销售订单", progress="38%", amount=68_000_000, delivery_date="2026-10-12", owner="李俊", risk_level="高", notes="客户变更交付节奏"),
        ]
        db.add_all(fulfillments)

    if db.query(FulfillmentMilestone).count() == 0:
        milestones = [
            FulfillmentMilestone(fulfill_id=1, milestone_name="合同签署完成", due_date="2026-04-20", status="完成", owner="张强", warning_level="正常", notes="已归档"),
            FulfillmentMilestone(fulfill_id=1, milestone_name="首批PO释放", due_date="2026-05-10", status="进行中", owner="张强", warning_level="正常", notes="等待客户财务审批"),
            FulfillmentMilestone(fulfill_id=2, milestone_name="核心驱动联调", due_date="2026-04-01", status="进行中", owner="刘海", warning_level="高", notes="已逾期，需加人推进"),
            FulfillmentMilestone(fulfill_id=3, milestone_name="试产验证报告", due_date="2026-04-15", status="未开始", owner="李健", warning_level="中", notes="预计本周启动"),
            FulfillmentMilestone(fulfill_id=5, milestone_name="客户出货窗口确认", due_date="2026-03-28", status="进行中", owner="李俊", warning_level="高", notes="客户窗口调整导致逾期"),
        ]
        db.add_all(milestones)

    db.commit()

