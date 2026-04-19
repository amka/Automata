# MIT License
#
# Copyright (c) 2026 Andrey Maksimov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# SPDX-License-Identifier: MIT

import threading
from pathlib import Path
from typing import Optional

from gi.repository import GLib
from loguru import logger

DB_PATH = Path(GLib.get_user_data_dir()) / "automata.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class DatabaseClient:
    _instance = None
    _lock = threading.Lock()
    _init_lock = threading.Lock()
    _db_path: str
    _thread_locals: threading.local

    def __new__(cls, db_path: Optional[str] = None):
        with cls._init_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._db_path = db_path or str(DB_PATH)
                cls._instance._thread_locals = threading.local()
                cls._instance._ensure_dir()
                cls._instance._initialize_schema()

            logger.info(f"Database initialized: {cls._instance._db_path}")
            return cls._instance

    def _ensure_dir(self):
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)

    def _get_conn(self) -> turso.Connection:
        """Thread-local connection to avoid check_same_thread issues"""
        if not hasattr(self._thread_locals, "conn") or self._thread_locals.conn is None:
            self._thread_locals.conn = turso.connect(self._db_path)
            self._configure_pragmas(self._thread_locals.conn)
        return self._thread_locals.conn

    def _configure_pragmas(self, conn: turso.Connection):
        """Optimize for concurrent reads + fast writes"""
        pragmas = [
            "PRAGMA journal_mode=WAL;",
            "PRAGMA synchronous=NORMAL;",
            "PRAGMA cache_size=-64000;",
            "PRAGMA foreign_keys=ON;",
            "PRAGMA busy_timeout=5000;",
        ]
        for p in pragmas:
            conn.execute(p)

    def _initialize_schema(self):
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                quadrant INTEGER NOT NULL DEFAULT 0,
                priority TEXT NOT NULL DEFAULT 'medium',
                due_date TEXT,
                tags TEXT DEFAULT '[]',
                assignee TEXT,
                project_id INTEGER,
                status TEXT NOT NULL DEFAULT 'active',
                created_at DATETIME DEFAULT (datetime('now')),
                updated_at DATETIME DEFAULT (datetime('now'))
            )
        """)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_tasks_quadrant_status ON tasks(quadrant, status)"
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)")
        conn.commit()
        logger.debug("Schema initialized")

    def execute(self, sql: str, params: tuple = ()) -> turso.Cursor:
        return self._get_conn().execute(sql, params)

    def commit(self):
        self._get_conn().commit()

    def close_all(self):
        """Graceful shutdown for all threads"""
        conn = self._get_conn()
        conn.close()
        self._thread_locals.conn = None
