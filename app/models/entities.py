"""数据库实体定义。"""

from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Customer(Base):
    """客户档案实体。"""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    customer_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    grade: Mapped[str] = mapped_column(String(2), default="B")
    region: Mapped[str] = mapped_column(String(32), default="华东")
    industry: Mapped[str] = mapped_column(String(32), default="消费电子")
    owner: Mapped[str] = mapped_column(String(32), default="系统")
    tags: Mapped[str] = mapped_column(String(255), default="")
    last_follow_up: Mapped[str] = mapped_column(String(32), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class Opportunity(Base):
    """商机实体。"""

    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    opp_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    opp_name: Mapped[str] = mapped_column(String(120), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    product_form: Mapped[str] = mapped_column(String(64), default="AR眼镜")
    product_line: Mapped[str] = mapped_column(String(64), default="XR")
    cooperation_mode: Mapped[str] = mapped_column(String(64), default="NRE")
    stage: Mapped[str] = mapped_column(String(32), default="stage3")
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    win_rate: Mapped[float] = mapped_column(Float, default=0.0)
    next_action: Mapped[str] = mapped_column(Text, default="")
    owner: Mapped[str] = mapped_column(String(32), default="系统")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class Lead(Base):
    """线索实体。"""

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lead_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    lead_name: Mapped[str] = mapped_column(String(120), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(120), default="")
    source: Mapped[str] = mapped_column(String(32), default="展会")
    region: Mapped[str] = mapped_column(String(32), default="中国区")
    product_direction: Mapped[str] = mapped_column(String(64), default="AR眼镜")
    priority: Mapped[str] = mapped_column(String(16), default="中")
    status: Mapped[str] = mapped_column(String(32), default="线索验证")
    owner: Mapped[str] = mapped_column(String(32), default="系统")
    contact: Mapped[str] = mapped_column(String(64), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    converted_opportunity_code: Mapped[str] = mapped_column(String(50), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class Fulfillment(Base):
    """履约实体。"""

    __tablename__ = "fulfillments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fulfill_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    project_name: Mapped[str] = mapped_column(String(120), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    stage: Mapped[str] = mapped_column(String(32), default="赢单阶段")
    progress: Mapped[str] = mapped_column(String(32), default="0%")
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    delivery_date: Mapped[str] = mapped_column(String(32), default="")
    owner: Mapped[str] = mapped_column(String(32), default="系统")
    risk_level: Mapped[str] = mapped_column(String(16), default="低")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class FulfillmentMilestone(Base):
    """履约里程碑实体。"""

    __tablename__ = "fulfillment_milestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fulfill_id: Mapped[int] = mapped_column(Integer, ForeignKey("fulfillments.id"), nullable=False, index=True)
    milestone_name: Mapped[str] = mapped_column(String(120), nullable=False)
    due_date: Mapped[str] = mapped_column(String(32), default="")
    status: Mapped[str] = mapped_column(String(16), default="未开始")
    owner: Mapped[str] = mapped_column(String(32), default="系统")
    warning_level: Mapped[str] = mapped_column(String(16), default="正常")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class AuditLog(Base):
    """操作审计日志实体。"""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    module: Mapped[str] = mapped_column(String(32), default="system")
    action: Mapped[str] = mapped_column(String(64), default="")
    operator: Mapped[str] = mapped_column(String(32), default="system")
    role: Mapped[str] = mapped_column(String(16), default="admin")
    target_id: Mapped[str] = mapped_column(String(64), default="")
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

