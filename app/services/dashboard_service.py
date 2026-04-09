"""看板服务层。"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.cache import cache
from app.core.logger import CRMLogger
from app.models.entities import Opportunity
from app.repositories.dashboard_repo import DashboardRepository


class DashboardService:
    """
    看板服务类（Service Pattern）。
    职责：聚合多个数据源并提供可视化可直接使用的数据结构。
    """

    CACHE_KEY = "dashboard:overview"

    @classmethod
    def get_overview(cls, db: Session) -> dict:
        """
        获取看板总览数据。
        使用缓存减少高频查询，提升并发场景下吞吐。
        """
        cached = cache.get(cls.CACHE_KEY)
        if cached:
            CRMLogger.info("DashboardService.get_overview", "命中缓存")
            return cached

        CRMLogger.info("DashboardService.get_overview", "缓存未命中，执行数据库聚合")
        total_amount = DashboardRepository.summary_amount(db)
        stage_totals = DashboardRepository.stage_totals(db)

        cards = [
            {"title": "2026总预测", "value": f"{total_amount / 1_000_000:.2f} M", "extra": "", "color": "#ff4d4f"},
            {"title": "2026已完成", "value": f"{(total_amount * 0.38) / 1_000_000:.2f} M", "extra": "", "color": "#1f6bff"},
            {"title": "stage6预测", "value": f"{(stage_totals.get('stage6', 0.0)) / 1_000_000:.2f} M", "extra": "", "color": "#222"},
            {"title": "stage5-4预测", "value": f"{(stage_totals.get('stage5', 0.0) + stage_totals.get('stage4', 0.0)) / 1_000_000:.2f} M", "extra": "", "color": "#222"},
            {"title": "stage3预测", "value": f"{(stage_totals.get('stage3', 0.0)) / 1_000_000:.2f} M", "extra": "", "color": "#222"},
            {"title": "Open PO 金额", "value": f"{(total_amount * 0.41) / 1_000_000:.2f} M", "extra": "", "color": "#52c41a"},
        ]

        data = {
            "cards": cards,
            "funnel": [
                {"name": "stage6", "value": stage_totals.get("stage6", 0.0)},
                {"name": "stage5", "value": stage_totals.get("stage5", 0.0)},
                {"name": "stage4", "value": stage_totals.get("stage4", 0.0)},
                {"name": "stage3", "value": stage_totals.get("stage3", 0.0)},
                {"name": "stage2", "value": stage_totals.get("stage2", 0.0)},
            ],
            "bu_trend": [
                {"bu": "D", "actual": 319_587_579, "stage6": 18_051_986, "stage5": 80_579_808},
                {"bu": "A", "actual": 279_772_083, "stage6": 693_445_770, "stage5": 16_891_522},
                {"bu": "B", "actual": 61_559_128, "stage6": 0, "stage5": 0},
                {"bu": "C", "actual": 229_043_370, "stage6": 267_859_518, "stage5": 55_159_267},
            ],
            "stage_progress": [
                {"name": "已完成", "value": total_amount * 0.35},
                {"name": "stage6", "value": stage_totals.get("stage6", 0.0)},
                {"name": "stage5-4", "value": stage_totals.get("stage5", 0.0) + stage_totals.get("stage4", 0.0)},
                {"name": "stage3", "value": stage_totals.get("stage3", 0.0)},
            ],
        }

        cache.set(cls.CACHE_KEY, data, ttl_seconds=30)
        return data

    @classmethod
    def get_drilldown(cls, db: Session, dimension: str = "owner", keyword: str | None = None) -> dict:
        """
        看板钻取数据（Drilldown）。
        dimension 支持 owner/stage/customer 三种，便于前端点击图表后联动明细表。
        """
        stmt = select(Opportunity).order_by(Opportunity.amount.desc())
        if keyword and dimension == "customer":
            stmt = stmt.where(Opportunity.customer_name.contains(keyword))
        rows = list(db.scalars(stmt))

        if dimension == "stage":
            bucket: dict[str, dict] = {}
            for item in rows:
                row = bucket.setdefault(item.stage, {"dimension": item.stage, "count": 0, "amount": 0.0})
                row["count"] += 1
                row["amount"] += float(item.amount)
            items = sorted(bucket.values(), key=lambda x: x["amount"], reverse=True)
        elif dimension == "customer":
            bucket = {}
            for item in rows:
                row = bucket.setdefault(item.customer_name, {"dimension": item.customer_name, "count": 0, "amount": 0.0})
                row["count"] += 1
                row["amount"] += float(item.amount)
            items = sorted(bucket.values(), key=lambda x: x["amount"], reverse=True)
        else:
            bucket = {}
            for item in rows:
                row = bucket.setdefault(item.owner, {"dimension": item.owner, "count": 0, "amount": 0.0})
                row["count"] += 1
                row["amount"] += float(item.amount)
            items = sorted(bucket.values(), key=lambda x: x["amount"], reverse=True)

        return {"dimension": dimension, "items": items[:20]}

    @classmethod
    def get_drilldown_details(cls, db: Session, dimension: str, value: str) -> dict:
        """
        看板钻取详情：返回命中该维度值的商机明细。
        用于前端点击“钻取汇总行”后弹窗展示。
        """
        stmt = select(Opportunity)
        if dimension == "stage":
            stmt = stmt.where(Opportunity.stage == value)
        elif dimension == "customer":
            stmt = stmt.where(Opportunity.customer_name == value)
        else:
            stmt = stmt.where(Opportunity.owner == value)

        rows = list(db.scalars(stmt.order_by(Opportunity.amount.desc()).limit(100)))
        items = [
            {
                "id": item.id,
                "opp_code": item.opp_code,
                "opp_name": item.opp_name,
                "customer_name": item.customer_name,
                "stage": item.stage,
                "amount": float(item.amount),
                "win_rate": float(item.win_rate),
                "owner": item.owner,
                "next_action": item.next_action,
            }
            for item in rows
        ]
        return {"dimension": dimension, "value": value, "items": items}

