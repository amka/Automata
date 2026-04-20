import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable

from gi.repository import GLib
from loguru import logger

from automata.models import Note, Project, Tag, Task


class DBWorker:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="DBWorker")
        self._initialized = False

    def _sync_init(self):
        """Синхронная инициализация Tortoise (выполняется в worker thread)"""
        if self._initialized:
            return

        # Синхронный запуск async init
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def _init():
            db_path = Path(GLib.get_user_data_dir()) / "automata.db"
            await Tortoise.init(
                config={
                    "connections": {
                        "default": {
                            "engine": "tortoise.backends.sqlite",
                            "credentials": {"file_path": db_path},
                        }
                    },
                    "apps": {
                        "models": {
                            "models": ["automata.models"],
                            "default_connection": "default",
                        }
                    },
                    "use_tz": False,
                }
            )
            await Tortoise.generate_schemas(safe=True)
            logger.debug("✅ Tortoise initialized in worker thread")

        loop.run_until_complete(_init())
        loop.close()
        self._initialized = True

    def _run_sync(self, coro_func: Callable, *args, **kwargs) -> Any:
        """Запускает async функцию Tortoise в потоке"""
        self._sync_init()  # гарантируем инициализацию

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(coro_func(*args, **kwargs))
            return result
        finally:
            loop.close()

    def execute(
        self, coro_func: Callable, callback: Callable[[Any], None], *args, **kwargs
    ):
        """Асинхронный запуск из GTK: coro_func — это async def из сервиса"""

        def worker():
            try:
                result = self._run_sync(coro_func, *args, **kwargs)
                GLib.idle_add(callback, result)
            except Exception as e:
                GLib.idle_add(self._error_callback, e)

        self.executor.submit(worker)

    def _error_callback(self, error):
        logger.debug(f"DB Error: {error}")
        # Можно показать Adw.Toast или диалог
        return False

    def shutdown(self):
        """Безопасное завершение при выходе из приложения"""
        logger.debug("🛑 Shutting down DB worker...")
        self.executor.shutdown(wait=True, cancel_futures=True)
        # Закрываем соединения синхронно
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(Tortoise.close_connections())
            loop.close()
        except Exception as e:
            logger.debug(f"Warning during DB close: {e}")


# Глобальный экземпляр
db_worker = DBWorker()
