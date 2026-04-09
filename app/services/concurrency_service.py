"""并发测试服务。"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from time import perf_counter, sleep
from app.core.logger import CRMLogger


class ConcurrencyService:
    """
    并发压测服务（Strategy Pattern 思想：可替换不同并发策略）。
    当前实现：线程池 + 互斥锁，演示高并发下共享资源安全更新。
    """

    _lock = Lock()
    _counter = 0

    @classmethod
    def _safe_increment(cls, delta: int) -> int:
        """受锁保护的计数器更新。"""
        sleep(0.01)
        with cls._lock:
            cls._counter += delta
            return cls._counter

    @classmethod
    def run_test(cls, workers: int = 20, tasks: int = 100) -> dict:
        """
        执行并发任务并返回统计结果。
        """
        start = perf_counter()
        cls._counter = 0
        results = []

        CRMLogger.info("ConcurrencyService.run_test", f"开始并发测试 workers={workers}, tasks={tasks}")

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(cls._safe_increment, 1) for _ in range(tasks)]
            for fut in as_completed(futures):
                results.append(fut.result())

        elapsed_ms = int((perf_counter() - start) * 1000)
        CRMLogger.info("ConcurrencyService.run_test", f"并发测试完成 elapsed_ms={elapsed_ms}")

        return {
            "workers": workers,
            "tasks": tasks,
            "elapsed_ms": elapsed_ms,
            "final_counter": cls._counter,
            "max_value_seen": max(results) if results else 0,
        }

