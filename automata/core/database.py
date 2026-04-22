from datetime import date

from loguru import logger

from automata.core.models import (  # импортируем из models.py
    BudgetEntry,
    Goal,
    KeyResult,
    Okr,
    Project,
    Task,
    db,
)


def init_db():
    """Initialize the database and create tables if they don't exist"""
    db.connect()
    with db:
        db.create_tables([Goal, Okr, KeyResult, Project, Task, BudgetEntry])
        db.execute_sql("CREATE INDEX IF NOT EXISTS idx_task_due ON tasks(due_date);")
        db.execute_sql(
            "CREATE INDEX IF NOT EXISTS idx_project_owner ON projects(owner);"
        )
    logger.debug("✅ Database initialized")
    return db


def close_db():
    """Close the database when exiting"""
    if not db.is_closed():
        db.close()
        logger.debug("✅ Database closed")
