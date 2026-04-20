from datetime import date

from loguru import logger
from peewee import SqliteDatabase

from automata.core.models import Note, Project, Task, db  # импортируем из models.py


def init_db():
    """Создаёт таблицы, если их нет"""
    db.connect()
    db.create_tables([Project, Task, Note], safe=True)
    logger.debug("✅ Peewee + SQLite инициализирован")
    if Project.select().count() == 0:
        Project.create(
            name="Пример: Миграция на новую базу данных",
            target_date=date(2026, 6, 30),
            order_index=0,
        )
    return db


def close_db():
    """Закрытие при выходе"""
    if not db.is_closed():
        db.close()
        logger.debug("✅ БД закрыта")
