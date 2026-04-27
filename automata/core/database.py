from loguru import logger

from automata.models import (  # импортируем из models.py
    INDEX_STATEMENTS,
    Attachment,
    BudgetEntry,
    BudgetLine,
    Commitment,
    EmailAccount,
    Goal,
    Initiative,
    ItemTag,
    Meeting,
    MeetingAttendee,
    MeetingNote,
    MeetingTemplate,
    Person,
    Project,
    Quarter,
    Tag,
    WorkItem,
    db,
)


def init_db():
    """Initialize the database and create tables if they don't exist"""
    db.connect()
    with db:
        db.create_tables(
            [
                Attachment,
                BudgetEntry,
                BudgetLine,
                Commitment,
                EmailAccount,
                Goal,
                Initiative,
                ItemTag,
                Meeting,
                MeetingAttendee,
                MeetingNote,
                MeetingTemplate,
                Person,
                Project,
                Quarter,
                Tag,
                WorkItem,
            ]
        )
        for stmt in INDEX_STATEMENTS:
            db.execute_sql(stmt)

    logger.debug("✅ Database initialized")
    return db


def close_db():
    """Close the database when exiting"""
    if not db.is_closed():
        db.close()
        logger.debug("✅ Database closed")
