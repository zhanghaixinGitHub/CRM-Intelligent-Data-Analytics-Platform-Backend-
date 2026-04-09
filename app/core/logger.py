"""统一日志模块。"""

import logging


class CRMLogger:
    """
    CRM 日志工具类。
    统一输出格式：`类名.方法名 >>> 日志信息`
    """

    _logger = logging.getLogger("crm_ai")
    _logger.setLevel(logging.INFO)
    if not _logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        _logger.addHandler(handler)

    @classmethod
    def info(cls, class_method: str, message: str) -> None:
        """输出 INFO 日志。"""
        cls._logger.info(f"{class_method} >>> {message}")

    @classmethod
    def error(cls, class_method: str, message: str) -> None:
        """输出 ERROR 日志。"""
        cls._logger.error(f"{class_method} >>> {message}")

