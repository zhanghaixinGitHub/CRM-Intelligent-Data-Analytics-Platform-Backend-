"""看板路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=ApiResponse)
def get_overview(db: Session = Depends(get_db)) -> ApiResponse:
    """获取看板总览数据。"""
    return ApiResponse(data=DashboardService.get_overview(db))


@router.get("/drilldown", response_model=ApiResponse)
def get_drilldown(
    dimension: str = "owner",
    keyword: str | None = None,
    db: Session = Depends(get_db),
) -> ApiResponse:
    """获取看板钻取数据。"""
    return ApiResponse(data=DashboardService.get_drilldown(db, dimension=dimension, keyword=keyword))


@router.get("/drilldown-details", response_model=ApiResponse)
def get_drilldown_details(
    dimension: str,
    value: str,
    db: Session = Depends(get_db),
) -> ApiResponse:
    """获取看板钻取详情明细。"""
    return ApiResponse(data=DashboardService.get_drilldown_details(db, dimension=dimension, value=value))

