"""通用响应模型。"""

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一响应结构。"""

    code: int = 0
    message: str = "success"
    data: dict | list | str | int | float | None = None

