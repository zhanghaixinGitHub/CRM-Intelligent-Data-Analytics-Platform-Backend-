"""分页模型。"""

from pydantic import BaseModel


class PageResponse(BaseModel):
    """统一分页响应结构。"""

    items: list[dict]
    total: int
    page: int
    page_size: int

