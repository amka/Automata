from datetime import datetime, timezone
from pathlib import Path

import peewee as pw
from gi.repository import GLib

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

    created_at = pw.DateTimeField(default=datetime.now(timezone.utc))
    updated_at = pw.DateTimeField(default=datetime.now(timezone.utc))

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)


# === 1. ГОДОВЫЕ ЦЕЛИ (Annual Goals) ===
class Goal(BaseModel):
    id = pw.AutoField()
    title = pw.CharField(max_length=255)
    description = pw.TextField(null=True)
    year = pw.IntegerField()  # например 2026
    target_value = pw.FloatField(null=True)  # если есть числовая цель
    current_value = pw.FloatField(default=0.0)
    owner = pw.CharField(max_length=100, null=True)  # твой ID или имя
    status = pw.CharField(
        choices=[
            ("active", "Active"),
            ("completed", "Completed"),
            ("paused", "Paused"),
        ],
        default="active",
    )

    # Health вычисляется автоматически при запросе (зелёный/жёлтый/красный)
    @property
    def progress(self):
        if not self.target_value or self.target_value == 0:
            return 0.0
        return min(100.0, (self.current_value / self.target_value) * 100)

    class Meta:
        table_name = "goals"


# === 2. КВАРТАЛЬНЫЕ OKR ===
class Okr(BaseModel):
    id = pw.AutoField()
    goal = pw.ForeignKeyField(Goal, backref="okrs", on_delete="CASCADE")  # каскад вниз
    quarter = pw.CharField(max_length=6)  # 'Q2-2026'
    objective = pw.CharField(max_length=255)
    description = pw.TextField(null=True)
    owner = pw.CharField(max_length=100, null=True)

    # Key Results будут отдельно или как JSON, но для простоты — отдельная модель ниже

    class Meta:
        table_name = "okrs"


class KeyResult(BaseModel):
    id = pw.AutoField()
    okr = pw.ForeignKeyField(Okr, backref="key_results", on_delete="CASCADE")
    title = pw.CharField(max_length=255)
    target = pw.FloatField()
    current = pw.FloatField(default=0.0)
    unit = pw.CharField(max_length=50, null=True)  # %, млн руб, шт и т.д.

    @property
    def progress(self):
        return min(100.0, (self.current / self.target) * 100) if self.target else 0.0

    class Meta:
        table_name = "key_results"


# === 3. ПРОЕКТЫ / ИНИЦИАТИВЫ (Portfolio) ===
class Project(BaseModel):
    id = pw.AutoField()
    okr = pw.ForeignKeyField(
        Okr, backref="projects", null=True, on_delete="SET NULL"
    )  # может быть без OKR на старте
    goal = pw.ForeignKeyField(Goal, backref="projects", null=True, on_delete="SET NULL")

    title = pw.CharField(max_length=255)
    description = pw.TextField(null=True)
    start_date = pw.DateField(null=True)
    end_date = pw.DateField(null=True)
    owner = pw.CharField(max_length=100)  # кто отвечает (директор направления)

    status = pw.CharField(
        choices=[
            ("not_started", "Not Started"),
            ("in_progress", "In Progress"),
            ("at_risk", "At Risk"),
            ("completed", "Completed"),
        ],
        default="not_started",
    )

    class Meta:
        table_name = "projects"

    @property
    def progress(self):
        # Авто-расчёт из задач (пример запроса ниже)
        tasks = self.tasks
        if not tasks:
            return 0.0
        completed = tasks.where(Task.status == "completed").count()
        return (completed / tasks.count()) * 100 if tasks.count() > 0 else 0.0


# === 4. ЗАДАЧИ (личные + делегированные) ===
class Task(BaseModel):
    id = pw.AutoField()
    project = pw.ForeignKeyField(
        Project, backref="tasks", null=True, on_delete="CASCADE"
    )
    okr = pw.ForeignKeyField(Okr, backref="tasks", null=True, on_delete="SET NULL")
    goal = pw.ForeignKeyField(Goal, backref="tasks", null=True, on_delete="SET NULL")

    title = pw.CharField(max_length=255)
    description = pw.TextField(null=True)
    assignee = pw.CharField(
        max_length=100, null=True
    )  # кто выполняет (ты или подчинённый)
    is_personal = pw.BooleanField(default=False)  # твои личные задачи без проекта

    due_date = pw.DateField(null=True)
    reminder_date = pw.DateField(null=True)

    status = pw.CharField(
        choices=[
            ("todo", "To Do"),
            ("in_progress", "In Progress"),
            ("blocked", "Blocked"),
            ("completed", "Completed"),
        ],
        default="todo",
    )
    priority = pw.IntegerField(default=0)  # 0-высокий, можно сортировать

    class Meta:
        table_name = "tasks"


# === 5. БЮДЖЕТ (сквозной слой) ===
class BudgetEntry(BaseModel):
    id = pw.AutoField()
    # Может быть привязан к любому уровню (гибко)
    goal = pw.ForeignKeyField(
        Goal, backref="budget_entries", null=True, on_delete="CASCADE"
    )
    okr = pw.ForeignKeyField(
        Okr, backref="budget_entries", null=True, on_delete="CASCADE"
    )
    project = pw.ForeignKeyField(
        Project, backref="budget_entries", null=True, on_delete="CASCADE"
    )
    task = pw.ForeignKeyField(
        Task, backref="budget_entries", null=True, on_delete="CASCADE"
    )

    allocated = pw.DecimalField(
        max_digits=15, decimal_places=2, default=0.0
    )  # запланировано
    spent = pw.DecimalField(max_digits=15, decimal_places=2, default=0.0)  # потрачено
    forecast = pw.DecimalField(max_digits=15, decimal_places=2, default=0.0)  # прогноз
    currency = pw.CharField(max_length=3, default="RUB")

    category = pw.CharField(
        max_length=100, null=True
    )  # например "Разработка", "Лицензии"
    note = pw.TextField(null=True)

    class Meta:
        table_name = "budget_entries"

    @property
    def variance(self):
        return self.allocated - self.spent
