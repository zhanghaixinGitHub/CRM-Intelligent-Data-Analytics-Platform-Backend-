"""FastAPI 应用入口。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.routes_ai import router as ai_router
from app.api.routes_customer import router as customer_router
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_fulfillment import router as fulfillment_router
from app.api.routes_lead import router as lead_router
from app.api.routes_opportunity import router as opportunity_router
from app.api.routes_system import router as system_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.logger import CRMLogger
from app.seed import init_seed_data

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """启动初始化：建表 + 预置数据。"""
    CRMLogger.info("Main.on_startup", "开始初始化数据库")
    Base.metadata.create_all(bind=engine)
    # 轻量迁移：兼容历史数据库缺少新字段的情况，避免因升级导致启动失败。
    with engine.connect() as conn:
        lead_cols = [row[1] for row in conn.execute(text("PRAGMA table_info(leads)")).fetchall()]
        if lead_cols and "converted_opportunity_code" not in lead_cols:
            conn.execute(text("ALTER TABLE leads ADD COLUMN converted_opportunity_code VARCHAR(50) DEFAULT ''"))
            conn.commit()

    db: Session = SessionLocal()
    try:
        init_seed_data(db)
    finally:
        db.close()
    CRMLogger.info("Main.on_startup", "数据库初始化完成")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(dashboard_router)
app.include_router(customer_router)
app.include_router(opportunity_router)
app.include_router(lead_router)
app.include_router(fulfillment_router)
app.include_router(ai_router)
app.include_router(system_router)

