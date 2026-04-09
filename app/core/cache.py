"""轻量内存缓存实现。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import RLock
from typing import Any


@dataclass
class CacheItem:
    """缓存条目。"""

    value: Any
    expire_at: datetime


class TTLMemoryCache:
    """
    线程安全的 TTL 内存缓存。

    这里使用 RLock 保证高并发下缓存读写安全，属于轻量化方案，
    不依赖 Redis 等外部中间件，适合你当前本地环境。
    """

    def __init__(self) -> None:
        self._store: dict[str, CacheItem] = {}
        self._lock = RLock()

    def set(self, key: str, value: Any, ttl_seconds: int = 30) -> None:
        """写入缓存，默认 30 秒过期。"""
        with self._lock:
            self._store[key] = CacheItem(
                value=value,
                expire_at=datetime.now() + timedelta(seconds=ttl_seconds),
            )

    def get(self, key: str) -> Any | None:
        """读取缓存，过期自动失效。"""
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            if datetime.now() > item.expire_at:
                self._store.pop(key, None)
                return None
            return item.value

    def clear(self) -> None:
        """清空缓存。"""
        with self._lock:
            self._store.clear()


cache = TTLMemoryCache()

