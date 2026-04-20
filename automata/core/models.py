from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

import peewee as pw
from gi.repository import GLib
from playhouse.sqlite_ext import JSONField

db_path = Path(GLib.get_user_data_dir()) / "automata.db"
# База данных
db = pw.SqliteDatabase(
    db_path,
    pragmas={
        "journal_mode": "wal",  # позволяет читать во время записи
        "cache_size": -64000,  # ~64 MB кэш
        "foreign_keys": 1,  # включить FK
        "busy_timeout": 30000,  # ждать 30 сек при блокировке
    },
)


class BaseModel(pw.Model):
    class Meta:
        database = db


class Project(BaseModel):
    name = pw.CharField(max_length=255, index=True)
    description = pw.TextField(null=True)
    status = pw.CharField(max_length=20, default="active")
    priority = pw.IntegerField(default=3)
    start_date = pw.DateField(null=True)
    target_date = pw.DateField(null=True)
    completed_at = pw.DateTimeField(null=True)
    progress = pw.FloatField(default=0.0)
    jira_board_key = pw.CharField(max_length=100, null=True)
    gitlab_group_id = pw.CharField(max_length=100, null=True)
    grafana_url = pw.CharField(max_length=500, null=True)

    created_at = pw.DateTimeField(default=datetime.now)
    updated_at = pw.DateTimeField(default=datetime.now)

    class Meta:
        table_name = "projects"


class Task(BaseModel):
    title = pw.CharField(max_length=500)
    description = pw.TextField(null=True)
    status = pw.CharField(max_length=20, default="todo")
    priority = pw.IntegerField(default=3)
    eisenhower = pw.CharField(max_length=20, null=True)
    due_date = pw.DateField(null=True)
    start_date = pw.DateField(null=True)
    completed_at = pw.DateTimeField(null=True)
    time_estimate = pw.IntegerField(null=True)  # минут
    time_spent = pw.IntegerField(default=0)

    project = pw.ForeignKeyField(
        Project, null=True, backref="tasks", on_delete="SET NULL"
    )
    parent_task = pw.ForeignKeyField(
        "self", null=True, backref="subtasks", on_delete="CASCADE"
    )

    jira_key = pw.CharField(max_length=50, null=True)
    incident_id = pw.CharField(max_length=100, null=True)
    tags = JSONField(default=list)  # список строк

    created_at = pw.DateTimeField(default=datetime.now)
    updated_at = pw.DateTimeField(default=datetime.now)

    class Meta:
        table_name = "tasks"


class Note(BaseModel):
    title = pw.CharField(max_length=255)
    content = pw.TextField()
    linked_type = pw.CharField(max_length=20, null=True)
    linked_id = pw.IntegerField(null=True)

    created_at = pw.DateTimeField(default=datetime.utcnow)
    updated_at = pw.DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "notes"
