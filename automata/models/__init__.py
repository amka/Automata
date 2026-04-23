from .schema import ALL_MODELS
from .schema import AppState
from .schema import Attachment
from .schema import BaseModel
from .schema import BudgetEntry
from .schema import BudgetLine
from .schema import Commitment
from .schema import DB_PATH
from .schema import EmailAccount
from .schema import Goal
from .schema import Initiative
from .schema import ItemTag
from .schema import Meeting
from .schema import MeetingAttendee
from .schema import MeetingNote
from .schema import MeetingTemplate
from .schema import Person
from .schema import Project
from .schema import Quarter
from .schema import SchemaVersion
from .schema import Tag
from .schema import WorkItem
from .schema import create_fts_support
from .schema import create_indexes
from .schema import create_tables
from .schema import create_updated_at_triggers
from .schema import create_views
from .schema import db
from .schema import initialize_schema

Task = WorkItem
Note = MeetingNote
TaskTag = ItemTag

__all__ = [
    "ALL_MODELS",
    "AppState",
    "Attachment",
    "BaseModel",
    "BudgetEntry",
    "BudgetLine",
    "Commitment",
    "DB_PATH",
    "EmailAccount",
    "Goal",
    "Initiative",
    "ItemTag",
    "Meeting",
    "MeetingAttendee",
    "MeetingNote",
    "MeetingTemplate",
    "Note",
    "Person",
    "Project",
    "Quarter",
    "SchemaVersion",
    "Tag",
    "Task",
    "TaskTag",
    "WorkItem",
    "create_fts_support",
    "create_indexes",
    "create_tables",
    "create_updated_at_triggers",
    "create_views",
    "db",
    "initialize_schema",
]
