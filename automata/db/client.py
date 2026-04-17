import os
from pathlib import Path

import turso
from gi.repository import GLib

DB_PATH = Path(GLib.get_user_data_dir()) / "automata.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    # libsql.sync поддерживает async API, идентичный sqlite3
    conn = turso.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            desc TEXT,
            quadrant INTEGER DEFAULT 0,  -- 0:Inbox 1:Do 2:Plan 3:Delegate 4:Drop
            priority TEXT DEFAULT 'medium',
            due_date TEXT,
            tags TEXT,
            assignee TEXT,
            project_id INTEGER,
            status TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT (datetime('now')),
            updated_at DATETIME DEFAULT (datetime('now'))
        )
    """)
    return conn
