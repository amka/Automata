# ui/task_loader.py
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from gi.repository import GLib
from loguru import logger

from automata.db.repo import TaskDAO


class TaskLoader:
    def __init__(self, dao: TaskDAO):
        self.dao = dao
        self._executor = ThreadPoolExecutor(max_workers=2)

    def load_async(
        self, quadrant=None, status="active", callback: Callable | None = None
    ):
        """Загружает задачи в фоне и вызывает callback в main-thread"""

        def _fetch():
            tasks = self.dao.get_all(quadrant=quadrant, status=status)
            logger.info(f"Loaded {len(tasks)} tasks for quadrant {quadrant}")
            if callback:
                GLib.idle_add(callback, tasks)

        self._executor.submit(_fetch)

    def complete_async(self, task_id: int, callback=None):
        def _update():
            self.dao.execute(
                "UPDATE tasks SET status='done', updated_at=datetime('now') WHERE id=?",
                (task_id,),
            )
            self.dao.commit()
            if callback:
                GLib.idle_add(callback, True)

        self._executor.submit(_update)

    def move_quadrant_async(
        self, task_id: int, quadrant: int, callback: Callable | None = None
    ):
        def _update():
            self.dao.execute(
                "UPDATE tasks SET quadrant=?, updated_at=datetime('now') WHERE id=?",
                (quadrant, task_id),
            )
            self.dao.commit()
            if callback:
                GLib.idle_add(callback, True)

        self._executor.submit(_update)
