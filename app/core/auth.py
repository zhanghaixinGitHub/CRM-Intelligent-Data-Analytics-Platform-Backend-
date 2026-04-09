"""轻量鉴权模块。"""

from fastapi import Header, HTTPException
from urllib.parse import unquote


ROLE_WEIGHT = {"sales": 1, "manager": 2, "director": 3, "admin": 4}


def get_current_user(
    x_user_name: str = Header(default="系统"),
    x_user_role: str = Header(default="admin"),
) -> dict:
    """从请求头读取用户身份，模拟真实项目中的网关透传用户上下文。"""
    # 前端会对中文用户名进行 URL 编码，这里统一解码，保证后续审计日志可读。
    decoded_user_name = unquote(x_user_name)
    role = x_user_role.lower()
    if role not in ROLE_WEIGHT:
        role = "sales"
    return {"name": decoded_user_name, "role": role}


def ensure_min_role(user: dict, min_role: str) -> None:
    """校验最小权限级别。"""
    if ROLE_WEIGHT.get(user["role"], 0) < ROLE_WEIGHT.get(min_role, 0):
        raise HTTPException(status_code=403, detail=f"当前角色无权限执行该操作，至少需要{min_role}")

