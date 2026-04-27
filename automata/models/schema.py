from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

import peewee as pw


def _resolve_db_path() -> Path:
    try:
        from gi.repository import GLib
    except Exception:
        data_home = os.environ.get("XDG_DATA_HOME")
        if data_home:
            return Path(data_home) / "automata.db"
        return Path.home() / ".local" / "share" / "automata.db"

    return Path(GLib.get_user_data_dir()) / "automata.db"


DB_PATH = _resolve_db_path()

db = pw.SqliteDatabase(
    str(DB_PATH),
    pragmas={
        "journal_mode": "wal",
        "synchronous": "normal",
        "foreign_keys": 1,
        "busy_timeout": 30000,
    },
)


class BaseModel(pw.Model):
    created_at = pw.DateTimeField(default=datetime.now(timezone.utc))
    updated_at = pw.DateTimeField(default=datetime.now(timezone.utc))

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)


class SchemaVersion(BaseModel):
    version = pw.IntegerField(primary_key=True)

    class Meta:
        table_name = "schema_version"


class AppState(BaseModel):
    key = pw.TextField(primary_key=True)
    value = pw.TextField(null=True)

    class Meta:
        table_name = "app_state"


class Person(BaseModel):
    id = pw.AutoField()
    name = pw.TextField()
    role = pw.TextField(null=True)
    email = pw.TextField(null=True, unique=True)
    team = pw.TextField(null=True)
    notes = pw.TextField(null=True)
    is_me = pw.BooleanField(
        default=False,
        constraints=[pw.Check("is_me IN (0, 1)")],
    )

    class Meta:
        table_name = "people"


class Goal(BaseModel):
    id = pw.AutoField()
    title = pw.TextField()
    description = pw.TextField(null=True)
    kpi_target = pw.FloatField(null=True)
    kpi_current = pw.FloatField(null=True)
    kpi_unit = pw.TextField(null=True)
    target_date = pw.TextField(null=True)
    status = pw.TextField(
        default="active",
        constraints=[
            pw.Check(
                "status IN ('active', 'achieved', 'at_risk', 'paused', 'cancelled')"
            )
        ],
    )
    color = pw.TextField(null=True)
    sort_order = pw.IntegerField(default=0)

    class Meta:
        table_name = "goals"


class Quarter(BaseModel):
    id = pw.AutoField()
    year = pw.IntegerField()
    q_number = pw.IntegerField(constraints=[pw.Check("q_number BETWEEN 1 AND 4")])
    start_date = pw.TextField()
    end_date = pw.TextField()
    focus_text = pw.TextField(null=True)

    class Meta:
        table_name = "quarters"
        indexes = ((("year", "q_number"), True),)


class Initiative(BaseModel):
    id = pw.AutoField()
    title = pw.TextField()
    goal = pw.ForeignKeyField(
        Goal,
        backref="initiatives",
        column_name="goal_id",
        null=True,
        on_delete="SET NULL",
    )
    quarter = pw.ForeignKeyField(
        Quarter,
        backref="initiatives",
        column_name="quarter_id",
        null=True,
        on_delete="SET NULL",
    )
    status = pw.TextField(
        default="active",
        constraints=[
            pw.Check("status IN ('active', 'completed', 'cancelled', 'on_hold')")
        ],
    )
    progress_pct = pw.IntegerField(
        null=True,
        constraints=[pw.Check("progress_pct BETWEEN 0 AND 100")],
    )

    class Meta:
        table_name = "initiatives"


class Project(BaseModel):
    id = pw.AutoField()
    title = pw.TextField()
    initiative = pw.ForeignKeyField(
        Initiative,
        backref="projects",
        column_name="initiative_id",
        null=True,
        on_delete="SET NULL",
    )
    quarter = pw.ForeignKeyField(
        Quarter,
        backref="projects",
        column_name="quarter_id",
        null=True,
        on_delete="SET NULL",
    )
    status = pw.TextField(
        default="idea",
        constraints=[
            pw.Check(
                "status IN ('idea', 'approval', 'execution', 'monitoring', 'completed', 'cancelled')"
            )
        ],
    )
    health = pw.TextField(
        null=True,
        constraints=[pw.Check("health IN ('green', 'yellow', 'red')")],
    )
    budget_plan = pw.FloatField(default=0)
    budget_fact = pw.FloatField(default=0)
    owner = pw.ForeignKeyField(
        Person,
        backref="owned_projects",
        column_name="owner_id",
        null=True,
        on_delete="SET NULL",
    )
    start_date = pw.TextField(null=True)
    end_date = pw.TextField(null=True)
    description = pw.TextField(null=True)

    class Meta:
        table_name = "projects"


class WorkItem(BaseModel):
    id = pw.AutoField()
    type = pw.TextField(
        constraints=[
            pw.Check(
                "type IN ('task', 'email', 'note', 'decision', 'idea', 'reference')"
            )
        ]
    )
    title = pw.TextField()
    body = pw.TextField(null=True)
    urgency = pw.IntegerField(default=0, constraints=[pw.Check("urgency IN (0, 1)")])
    importance = pw.IntegerField(
        default=0,
        constraints=[pw.Check("importance IN (0, 1)")],
    )
    status = pw.TextField(
        default="inbox",
        constraints=[
            pw.Check(
                "status IN ('inbox', 'todo', 'waiting', 'scheduled', 'done', 'archived', 'delegated')"
            )
        ],
    )
    project = pw.ForeignKeyField(
        Project,
        backref="work_items",
        column_name="project_id",
        null=True,
        on_delete="SET NULL",
    )
    owner = pw.ForeignKeyField(
        Person,
        backref="work_items",
        column_name="owner_id",
        null=True,
        on_delete="SET NULL",
    )
    due_date = pw.TextField(null=True)
    scheduled_date = pw.TextField(null=True)
    completed_at = pw.TextField(null=True)
    external_ref = pw.TextField(null=True)
    source = pw.TextField(default="manual")
    deleted_at = pw.TextField(null=True)

    class Meta:
        table_name = "work_items"


class Commitment(BaseModel):
    id = pw.AutoField()
    work_item = pw.ForeignKeyField(
        WorkItem,
        backref="commitments",
        column_name="work_item_id",
        null=True,
        on_delete="SET NULL",
    )
    from_person = pw.ForeignKeyField(
        Person,
        backref="outgoing_commitments",
        column_name="from_person_id",
        on_delete="RESTRICT",
    )
    to_person = pw.ForeignKeyField(
        Person,
        backref="incoming_commitments",
        column_name="to_person_id",
        on_delete="RESTRICT",
    )
    title = pw.TextField()
    promised_date = pw.TextField(null=True)
    due_date = pw.TextField()
    status = pw.TextField(
        default="active",
        constraints=[
            pw.Check(
                "status IN ('active', 'fulfilled', 'breached', 'renegotiated', 'cancelled')"
            )
        ],
    )
    fulfillment_date = pw.TextField(null=True)
    notes = pw.TextField(null=True)
    reminder_sent = pw.BooleanField(
        default=False,
        constraints=[pw.Check("reminder_sent IN (0, 1)")],
    )

    class Meta:
        table_name = "commitments"
        constraints = [pw.Check("from_person_id != to_person_id")]


class MeetingTemplate(BaseModel):
    id = pw.AutoField()
    name = pw.TextField()
    type = pw.TextField(
        constraints=[
            pw.Check("type IN ('1on1', 'strategic', 'ops', 'ad_hoc', 'review')")
        ]
    )
    agenda_markdown = pw.TextField()
    is_default = pw.BooleanField(
        default=False,
        constraints=[pw.Check("is_default IN (0, 1)")],
    )

    class Meta:
        table_name = "meeting_templates"


class Meeting(BaseModel):
    id = pw.AutoField()
    title = pw.TextField()
    meeting_date = pw.TextField()
    type = pw.TextField(
        constraints=[
            pw.Check("type IN ('1on1', 'strategic', 'ops', 'ad_hoc', 'review')")
        ]
    )
    project = pw.ForeignKeyField(
        Project,
        backref="meetings",
        column_name="project_id",
        null=True,
        on_delete="SET NULL",
    )
    template = pw.ForeignKeyField(
        MeetingTemplate,
        backref="meetings",
        column_name="template_id",
        null=True,
        on_delete="SET NULL",
    )
    agenda = pw.TextField(null=True)
    notes = pw.TextField(null=True)

    class Meta:
        table_name = "meetings"


class MeetingAttendee(BaseModel):
    meeting = pw.ForeignKeyField(
        Meeting,
        backref="attendees",
        column_name="meeting_id",
        on_delete="CASCADE",
    )
    person = pw.ForeignKeyField(
        Person,
        backref="meeting_attendances",
        column_name="person_id",
        on_delete="CASCADE",
    )
    role = pw.TextField(
        default="attendee",
        constraints=[pw.Check("role IN ('attendee', 'organizer', 'note_taker')")],
    )

    class Meta:
        table_name = "meeting_attendees"
        primary_key = pw.CompositeKey("meeting", "person")


class MeetingNote(BaseModel):
    id = pw.AutoField()
    meeting = pw.ForeignKeyField(
        Meeting,
        backref="captured_notes",
        column_name="meeting_id",
        on_delete="CASCADE",
    )
    person = pw.ForeignKeyField(
        Person,
        backref="meeting_notes",
        column_name="person_id",
        null=True,
        on_delete="SET NULL",
    )
    note_text = pw.TextField()
    is_decision = pw.BooleanField(
        default=False,
        constraints=[pw.Check("is_decision IN (0, 1)")],
    )
    is_action_item = pw.BooleanField(
        default=False,
        constraints=[pw.Check("is_action_item IN (0, 1)")],
    )
    linked_work_item = pw.ForeignKeyField(
        WorkItem,
        backref="meeting_notes",
        column_name="linked_work_item_id",
        null=True,
        on_delete="SET NULL",
    )

    class Meta:
        table_name = "meeting_notes"


class BudgetLine(BaseModel):
    id = pw.AutoField()
    name = pw.TextField()
    type = pw.TextField(constraints=[pw.Check("type IN ('capex', 'opex')")])
    annual_plan = pw.FloatField(default=0)
    q1_plan = pw.FloatField(default=0)
    q2_plan = pw.FloatField(default=0)
    q3_plan = pw.FloatField(default=0)
    q4_plan = pw.FloatField(default=0)
    description = pw.TextField(null=True)

    class Meta:
        table_name = "budget_lines"


class BudgetEntry(BaseModel):
    id = pw.AutoField()
    project = pw.ForeignKeyField(
        Project,
        backref="budget_entries",
        column_name="project_id",
        null=True,
        on_delete="SET NULL",
    )
    budget_line = pw.ForeignKeyField(
        BudgetLine,
        backref="entries",
        column_name="budget_line_id",
        on_delete="RESTRICT",
    )
    amount = pw.FloatField()
    entry_date = pw.TextField()
    description = pw.TextField(null=True)
    entry_type = pw.TextField(constraints=[pw.Check("entry_type IN ('plan', 'fact')")])
    quarter = pw.IntegerField(
        null=True,
        constraints=[pw.Check("quarter BETWEEN 1 AND 4")],
    )

    class Meta:
        table_name = "budget_entries"


class Tag(BaseModel):
    id = pw.AutoField()
    name = pw.TextField(unique=True)
    color = pw.TextField(null=True)

    class Meta:
        table_name = "tags"


class ItemTag(BaseModel):
    item = pw.ForeignKeyField(
        WorkItem,
        backref="item_tags",
        column_name="item_id",
        on_delete="CASCADE",
    )
    tag = pw.ForeignKeyField(
        Tag,
        backref="item_tags",
        column_name="tag_id",
        on_delete="CASCADE",
    )

    class Meta:
        table_name = "item_tags"
        primary_key = pw.CompositeKey("item", "tag")


class Attachment(BaseModel):
    id = pw.AutoField()
    work_item = pw.ForeignKeyField(
        WorkItem,
        backref="attachments",
        column_name="work_item_id",
        null=True,
        on_delete="CASCADE",
    )
    meeting = pw.ForeignKeyField(
        Meeting,
        backref="attachments",
        column_name="meeting_id",
        null=True,
        on_delete="CASCADE",
    )
    file_name = pw.TextField()
    file_path = pw.TextField()
    file_size = pw.IntegerField(null=True)
    mime_type = pw.TextField(null=True)

    class Meta:
        table_name = "attachments"


class EmailAccount(BaseModel):
    id = pw.AutoField()
    name = pw.TextField()
    email = pw.TextField()
    imap_server = pw.TextField(null=True)
    imap_port = pw.IntegerField(default=993)
    smtp_server = pw.TextField(null=True)
    smtp_port = pw.IntegerField(default=587)
    username = pw.TextField(null=True)
    use_ssl = pw.BooleanField(
        default=True,
        constraints=[pw.Check("use_ssl IN (0, 1)")],
    )
    is_active = pw.BooleanField(
        default=True,
        constraints=[pw.Check("is_active IN (0, 1)")],
    )
    last_sync_at = pw.TextField(null=True)

    class Meta:
        table_name = "email_accounts"


ALL_MODELS: Final[tuple[type[pw.Model], ...]] = (
    SchemaVersion,
    AppState,
    Person,
    Goal,
    Quarter,
    Initiative,
    Project,
    WorkItem,
    Commitment,
    MeetingTemplate,
    Meeting,
    MeetingAttendee,
    MeetingNote,
    BudgetLine,
    BudgetEntry,
    Tag,
    ItemTag,
    Attachment,
    EmailAccount,
)

INDEX_STATEMENTS: Final[tuple[str, ...]] = (
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_people_is_me ON people(is_me) WHERE is_me = 1;",
    "CREATE INDEX IF NOT EXISTS idx_work_items_status ON work_items(status);",
    "CREATE INDEX IF NOT EXISTS idx_work_items_due ON work_items(due_date) WHERE deleted_at IS NULL;",
    "CREATE INDEX IF NOT EXISTS idx_work_items_project ON work_items(project_id);",
    "CREATE INDEX IF NOT EXISTS idx_work_items_owner ON work_items(owner_id);",
    "CREATE INDEX IF NOT EXISTS idx_work_items_matrix ON work_items(urgency, importance, status) WHERE status NOT IN ('done', 'archived') AND deleted_at IS NULL;",
    "CREATE INDEX IF NOT EXISTS idx_commitments_from ON commitments(from_person_id, status);",
    "CREATE INDEX IF NOT EXISTS idx_commitments_to ON commitments(to_person_id, status);",
    "CREATE INDEX IF NOT EXISTS idx_commitments_due ON commitments(due_date) WHERE status = 'active';",
    "CREATE INDEX IF NOT EXISTS idx_commitments_work_item ON commitments(work_item_id);",
    "CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);",
    "CREATE INDEX IF NOT EXISTS idx_projects_health ON projects(health);",
    "CREATE INDEX IF NOT EXISTS idx_projects_quarter ON projects(quarter_id);",
    "CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(owner_id);",
    "CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(meeting_date);",
    "CREATE INDEX IF NOT EXISTS idx_meetings_type ON meetings(type);",
    "CREATE INDEX IF NOT EXISTS idx_meeting_notes_meeting ON meeting_notes(meeting_id);",
    "CREATE INDEX IF NOT EXISTS idx_meeting_notes_person ON meeting_notes(person_id);",
    "CREATE INDEX IF NOT EXISTS idx_budget_entries_project ON budget_entries(project_id);",
    "CREATE INDEX IF NOT EXISTS idx_budget_entries_line ON budget_entries(budget_line_id);",
)

UPDATED_AT_TRIGGER_STATEMENTS: Final[tuple[str, ...]] = (
    """CREATE TRIGGER IF NOT EXISTS trg_work_items_updated
AFTER UPDATE ON work_items BEGIN
    UPDATE work_items SET updated_at = datetime('now') WHERE id = NEW.id;
END;""",
    """CREATE TRIGGER IF NOT EXISTS trg_commitments_updated
AFTER UPDATE ON commitments BEGIN
    UPDATE commitments SET updated_at = datetime('now') WHERE id = NEW.id;
END;""",
    """CREATE TRIGGER IF NOT EXISTS trg_projects_updated
AFTER UPDATE ON projects BEGIN
    UPDATE projects SET updated_at = datetime('now') WHERE id = NEW.id;
END;""",
    """CREATE TRIGGER IF NOT EXISTS trg_goals_updated
AFTER UPDATE ON goals BEGIN
    UPDATE goals SET updated_at = datetime('now') WHERE id = NEW.id;
END;""",
)

FTS_STATEMENTS: Final[tuple[str, ...]] = (
    """CREATE VIRTUAL TABLE IF NOT EXISTS work_items_fts USING fts5(
    title, body,
    content='work_items',
    content_rowid='id'
);""",
    """CREATE TRIGGER IF NOT EXISTS trg_work_items_fts_insert
AFTER INSERT ON work_items BEGIN
    INSERT INTO work_items_fts(rowid, title, body)
    VALUES (NEW.id, NEW.title, NEW.body);
END;""",
    """CREATE TRIGGER IF NOT EXISTS trg_work_items_fts_delete
AFTER DELETE ON work_items BEGIN
    INSERT INTO work_items_fts(work_items_fts, rowid, title, body)
    VALUES ('delete', OLD.id, OLD.title, OLD.body);
END;""",
    """CREATE TRIGGER IF NOT EXISTS trg_work_items_fts_update
AFTER UPDATE ON work_items BEGIN
    INSERT INTO work_items_fts(work_items_fts, rowid, title, body)
    VALUES ('delete', OLD.id, OLD.title, OLD.body);
    INSERT INTO work_items_fts(rowid, title, body)
    VALUES (NEW.id, NEW.title, NEW.body);
END;""",
)

VIEW_STATEMENTS: Final[tuple[str, ...]] = (
    """CREATE VIEW IF NOT EXISTS v_my_commitments AS
SELECT
    c.id,
    c.title,
    c.due_date,
    c.status,
    p_to.name AS to_person,
    w.type AS work_item_type,
    CASE
        WHEN date(c.due_date) < date('now') THEN 'overdue'
        WHEN date(c.due_date) = date('now') THEN 'today'
        ELSE 'future'
    END AS urgency_flag
FROM commitments c
JOIN people p_me ON c.from_person_id = p_me.id
JOIN people p_to ON c.to_person_id = p_to.id
LEFT JOIN work_items w ON c.work_item_id = w.id
WHERE p_me.is_me = 1 AND c.status = 'active';""",
    """CREATE VIEW IF NOT EXISTS v_their_commitments AS
SELECT
    c.id,
    c.title,
    c.due_date,
    c.status,
    p_from.name AS from_person,
    w.type AS work_item_type,
    CASE
        WHEN date(c.due_date) < date('now') THEN 'overdue'
        WHEN date(c.due_date) = date('now') THEN 'today'
        ELSE 'future'
    END AS urgency_flag
FROM commitments c
JOIN people p_me ON c.to_person_id = p_me.id
JOIN people p_from ON c.from_person_id = p_from.id
LEFT JOIN work_items w ON c.work_item_id = w.id
WHERE p_me.is_me = 1 AND c.status = 'active';""",
    """CREATE VIEW IF NOT EXISTS v_today_matrix AS
SELECT
    id,
    type,
    title,
    status,
    due_date,
    project_id,
    urgency,
    importance,
    CASE
        WHEN urgency = 1 AND importance = 1 THEN 'do'
        WHEN urgency = 0 AND importance = 1 THEN 'schedule'
        WHEN urgency = 1 AND importance = 0 THEN 'delegate'
        ELSE 'eliminate'
    END AS quadrant
FROM work_items
WHERE status NOT IN ('done', 'archived')
  AND deleted_at IS NULL
ORDER BY
    urgency DESC,
    importance DESC,
    due_date ASC;""",
    """CREATE VIEW IF NOT EXISTS v_project_portfolio AS
SELECT
    p.id,
    p.title,
    p.status,
    p.health,
    p.owner_id,
    pe.name AS owner_name,
    p.budget_plan,
    p.budget_fact,
    ROUND((p.budget_fact / NULLIF(p.budget_plan, 0)) * 100, 1) AS budget_pct,
    i.title AS initiative_title,
    g.title AS goal_title,
    q.year || '-Q' || q.q_number AS quarter_label
FROM projects p
LEFT JOIN people pe ON p.owner_id = pe.id
LEFT JOIN initiatives i ON p.initiative_id = i.id
LEFT JOIN goals g ON i.goal_id = g.id
LEFT JOIN quarters q ON p.quarter_id = q.id
WHERE p.status != 'cancelled';""",
    """CREATE VIEW IF NOT EXISTS v_budget_status AS
SELECT
    bl.id,
    bl.name,
    bl.type,
    bl.annual_plan,
    COALESCE(SUM(CASE WHEN be.entry_type = 'fact' THEN be.amount ELSE 0 END), 0) AS total_fact,
    bl.annual_plan - COALESCE(SUM(CASE WHEN be.entry_type = 'fact' THEN be.amount ELSE 0 END), 0) AS remaining
FROM budget_lines bl
LEFT JOIN budget_entries be ON bl.id = be.budget_line_id
GROUP BY bl.id;""",
)


def _execute_sql_batch(statements: tuple[str, ...]) -> None:
    for statement in statements:
        db.execute_sql(statement)


def create_tables(safe: bool = True) -> None:
    db.create_tables(list(ALL_MODELS), safe=safe)


def create_indexes() -> None:
    _execute_sql_batch(INDEX_STATEMENTS)


def create_updated_at_triggers() -> None:
    _execute_sql_batch(UPDATED_AT_TRIGGER_STATEMENTS)


def create_fts_support() -> None:
    _execute_sql_batch(FTS_STATEMENTS)


def create_views() -> None:
    _execute_sql_batch(VIEW_STATEMENTS)


def initialize_schema(
    *,
    include_views: bool = True,
    include_fts: bool = True,
    safe: bool = True,
) -> None:
    db.connect(reuse_if_open=True)
    create_tables(safe=safe)
    create_indexes()
    create_updated_at_triggers()
    if include_fts:
        create_fts_support()
    if include_views:
        create_views()


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
    "INDEX_STATEMENTS",
    "Initiative",
    "ItemTag",
    "Meeting",
    "MeetingAttendee",
    "MeetingNote",
    "MeetingTemplate",
    "Person",
    "Project",
    "Quarter",
    "SchemaVersion",
    "Tag",
    "VIEW_STATEMENTS",
    "WorkItem",
    "create_fts_support",
    "create_indexes",
    "create_tables",
    "create_updated_at_triggers",
    "create_views",
    "db",
    "initialize_schema",
]
