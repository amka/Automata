**Automata**

Ниже — полная проработка модели данных, где **Commitment** — это не просто поле, а центральная сущность, связывающая людей, работу и время. Схема рассчитана на SQLite, Python и local-first архитектуру.

---

## 1. Философия модели: Commitment-First

В классических таск-трекерах доминирует **задача** (Task). В Automata доминирует **обязательство** (Commitment) — социальный контракт между двумя людьми с дедлайном и статусом.

```
WorkItem (что нужно сделать)
    └── может порождать → Commitment (кто кому обещал)
            └── от Person A к Person B
            └── с дедлайном и статусом исполнения
```

**Почему это работает для C-level:**
- Вы не управляете 500 задачами команды. Вы управляете 30-50 обязательствами, где **ваше вмешательство** критично.
- «Делегировать» в Automata = создать Commitment с дедлайном. Система следит за ним, а не за подзадачами в Jira.
- Любое письмо, встреча или заметка может породить Commitment — и вы всегда видите «кто что мне должен» и «что я кому должен».

---

## 2. Entity Relationship (текстовая диаграмма)

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│   people    │◄──────┤  commitments    │──────►│   people    │
│  (from)     │       │                 │       │    (to)     │
└─────────────┘       │  work_item_id ──┼──────►├─────────────┤
                      │  due_date       │       │ work_items  │
┌─────────────┐       │  status         │       │             │
│    goals    │◄──────┘                 │       │  type       │
└──────┬──────┘                         │       │  status     │
       │                                │       │  matrix     │
┌──────▼──────┐       ┌─────────────────┤       └─────────────┘
│ initiatives │◄──────┤    meetings     │
└──────┬──────┘       │                 │
       │              │  attendees (M2M)│
┌──────▼──────┐       └─────────────────┘
│   projects  │◄──────────────┐
└──────┬──────┘               │
       │                      │
┌──────▼──────┐       ┌───────▼───────┐
budget_entries│       │ meeting_notes │
└─────────────┘       └───────────────┘
```

---

## 3. Полная SQL-схема (`schema.sql`)

Файл готов к использованию. Все даты — ISO8601 (`TEXT`), булевы значения — `INTEGER` (0/1).

```sql
-- ============================================================
-- AUTOMATA v1.0 — Local-first C-level Operating System
-- ============================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- Миграции
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Состояние приложения (текущий пользователь, настройки)
CREATE TABLE IF NOT EXISTS app_state (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- 1. PEOPLE — справочник людей
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT,
    email TEXT,
    team TEXT,
    notes TEXT,
    is_me INTEGER NOT NULL DEFAULT 0 CHECK(is_me IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(email) WHERE email IS NOT NULL
);

-- Только один "я"
CREATE UNIQUE INDEX IF NOT EXISTS idx_people_is_me ON people(is_me) WHERE is_me = 1;

-- -----------------------------------------------------------
-- 2. GOALS — стратегические цели (годовые)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    kpi_target REAL,
    kpi_current REAL,
    kpi_unit TEXT,
    target_date TEXT,
    status TEXT NOT NULL DEFAULT 'active' 
        CHECK(status IN ('active', 'achieved', 'at_risk', 'paused', 'cancelled')),
    color TEXT, -- hex, например "#3584e4"
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- 3. QUARTERS — кварталы
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS quarters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    q_number INTEGER NOT NULL CHECK(q_number BETWEEN 1 AND 4),
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    focus_text TEXT,
    UNIQUE(year, q_number)
);

-- -----------------------------------------------------------
-- 4. INITIATIVES — инициативы (связка цель + квартал)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS initiatives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    goal_id INTEGER REFERENCES goals(id) ON DELETE SET NULL,
    quarter_id INTEGER REFERENCES quarters(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'active' 
        CHECK(status IN ('active', 'completed', 'cancelled', 'on_hold')),
    progress_pct INTEGER CHECK(progress_pct BETWEEN 0 AND 100),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- 5. PROJECTS — проекты
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    initiative_id INTEGER REFERENCES initiatives(id) ON DELETE SET NULL,
    quarter_id INTEGER REFERENCES quarters(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'idea' 
        CHECK(status IN ('idea', 'approval', 'execution', 'monitoring', 'completed', 'cancelled')),
    health TEXT CHECK(health IN ('green', 'yellow', 'red')),
    budget_plan REAL NOT NULL DEFAULT 0,
    budget_fact REAL NOT NULL DEFAULT 0,
    owner_id INTEGER REFERENCES people(id) ON DELETE SET NULL,
    start_date TEXT,
    end_date TEXT,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- 6. WORK_ITEMS — единый вход: задачи, письма, заметки, решения
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS work_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL 
        CHECK(type IN ('task', 'email', 'note', 'decision', 'idea', 'reference')),
    title TEXT NOT NULL,
    body TEXT,
    urgency INTEGER NOT NULL DEFAULT 0 CHECK(urgency IN (0, 1)),
    importance INTEGER NOT NULL DEFAULT 0 CHECK(importance IN (0, 1)),
    status TEXT NOT NULL DEFAULT 'inbox' 
        CHECK(status IN ('inbox', 'todo', 'waiting', 'scheduled', 'done', 'archived', 'delegated')),
    project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    owner_id INTEGER REFERENCES people(id) ON DELETE SET NULL,
    due_date TEXT,
    scheduled_date TEXT,
    completed_at TEXT,
    external_ref TEXT, -- ссылка на Jira, ID письма и т.п.
    source TEXT DEFAULT 'manual', -- 'manual', 'email', 'import'
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    deleted_at TEXT  -- soft delete
);

-- -----------------------------------------------------------
-- 7. COMMITMENTS — обязательства (ЦЕНТРАЛЬНАЯ СУЩНОСТЬ)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS commitments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_item_id INTEGER REFERENCES work_items(id) ON DELETE SET NULL,
    from_person_id INTEGER NOT NULL REFERENCES people(id),
    to_person_id INTEGER NOT NULL REFERENCES people(id),
    title TEXT NOT NULL, -- денормализовано для быстрого отображения
    promised_date TEXT, -- когда взяли в работу/пообещали
    due_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' 
        CHECK(status IN ('active', 'fulfilled', 'breached', 'renegotiated', 'cancelled')),
    fulfillment_date TEXT,
    notes TEXT,
    reminder_sent INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    CHECK(from_person_id != to_person_id)
);

-- -----------------------------------------------------------
-- 8. MEETINGS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    meeting_date TEXT NOT NULL,
    type TEXT NOT NULL 
        CHECK(type IN ('1on1', 'strategic', 'ops', 'ad_hoc', 'review')),
    project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    template_id INTEGER REFERENCES meeting_templates(id),
    agenda TEXT, -- markdown
    notes TEXT, -- markdown
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- 9. MEETING_TEMPLATES
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS meeting_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL 
        CHECK(type IN ('1on1', 'strategic', 'ops', 'ad_hoc', 'review')),
    agenda_markdown TEXT NOT NULL,
    is_default INTEGER DEFAULT 0
);

-- -----------------------------------------------------------
-- 10. MEETING_ATTENDEES
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS meeting_attendees (
    meeting_id INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    person_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'attendee' CHECK(role IN ('attendee', 'organizer', 'note_taker')),
    PRIMARY KEY (meeting_id, person_id)
);

-- -----------------------------------------------------------
-- 11. MEETING_NOTES — захват во время встреч
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS meeting_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    person_id INTEGER REFERENCES people(id) ON DELETE SET NULL, -- о ком заметка
    note_text TEXT NOT NULL,
    is_decision INTEGER DEFAULT 0,
    is_action_item INTEGER DEFAULT 0,
    linked_work_item_id INTEGER REFERENCES work_items(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- 12. BUDGET_LINES — статьи бюджета
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS budget_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('capex', 'opex')),
    annual_plan REAL NOT NULL DEFAULT 0,
    q1_plan REAL DEFAULT 0,
    q2_plan REAL DEFAULT 0,
    q3_plan REAL DEFAULT 0,
    q4_plan REAL DEFAULT 0,
    description TEXT
);

-- -----------------------------------------------------------
-- 13. BUDGET_ENTRIES — проводки план/факт
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS budget_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    budget_line_id INTEGER NOT NULL REFERENCES budget_lines(id),
    amount REAL NOT NULL,
    entry_date TEXT NOT NULL,
    description TEXT,
    entry_type TEXT NOT NULL CHECK(entry_type IN ('plan', 'fact')),
    quarter INTEGER CHECK(quarter BETWEEN 1 AND 4),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- 14. TAGS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT
);

CREATE TABLE IF NOT EXISTS item_tags (
    item_id INTEGER NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, tag_id)
);

-- -----------------------------------------------------------
-- 15. ATTACHMENTS
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_item_id INTEGER REFERENCES work_items(id) ON DELETE CASCADE,
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    mime_type TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------
-- 16. EMAIL_ACCOUNTS (для IMAP/SMTP)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS email_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    imap_server TEXT,
    imap_port INTEGER DEFAULT 993,
    smtp_server TEXT,
    smtp_port INTEGER DEFAULT 587,
    username TEXT,
    -- пароль хранится в libsecret, не здесь
    use_ssl INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    last_sync_at TEXT
);

-- -----------------------------------------------------------
-- ИНДЕКСЫ
-- -----------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_work_items_status ON work_items(status);
CREATE INDEX IF NOT EXISTS idx_work_items_due ON work_items(due_date) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_work_items_project ON work_items(project_id);
CREATE INDEX IF NOT EXISTS idx_work_items_owner ON work_items(owner_id);
CREATE INDEX IF NOT EXISTS idx_work_items_matrix ON work_items(urgency, importance, status) 
    WHERE status NOT IN ('done', 'archived') AND deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_commitments_from ON commitments(from_person_id, status);
CREATE INDEX IF NOT EXISTS idx_commitments_to ON commitments(to_person_id, status);
CREATE INDEX IF NOT EXISTS idx_commitments_due ON commitments(due_date) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_commitments_work_item ON commitments(work_item_id);

CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_health ON projects(health);
CREATE INDEX IF NOT EXISTS idx_projects_quarter ON projects(quarter_id);
CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(owner_id);

CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(meeting_date);
CREATE INDEX IF NOT EXISTS idx_meetings_type ON meetings(type);
CREATE INDEX IF NOT EXISTS idx_meeting_notes_meeting ON meeting_notes(meeting_id);
CREATE INDEX IF NOT EXISTS idx_meeting_notes_person ON meeting_notes(person_id);

CREATE INDEX IF NOT EXISTS idx_budget_entries_project ON budget_entries(project_id);
CREATE INDEX IF NOT EXISTS idx_budget_entries_line ON budget_entries(budget_line_id);

-- -----------------------------------------------------------
-- ТРИГГЕРЫ updated_at
-- -----------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_work_items_updated 
AFTER UPDATE ON work_items BEGIN
    UPDATE work_items SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_commitments_updated 
AFTER UPDATE ON commitments BEGIN
    UPDATE commitments SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_projects_updated 
AFTER UPDATE ON projects BEGIN
    UPDATE projects SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_goals_updated 
AFTER UPDATE ON goals BEGIN
    UPDATE goals SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- -----------------------------------------------------------
-- FTS5 для полнотекстового поиска
-- -----------------------------------------------------------
CREATE VIRTUAL TABLE IF NOT EXISTS work_items_fts USING fts5(
    title, body, 
    content='work_items', 
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS trg_work_items_fts_insert 
AFTER INSERT ON work_items BEGIN
    INSERT INTO work_items_fts(rowid, title, body) 
    VALUES (NEW.id, NEW.title, NEW.body);
END;

CREATE TRIGGER IF NOT EXISTS trg_work_items_fts_delete 
AFTER DELETE ON work_items BEGIN
    INSERT INTO work_items_fts(work_items_fts, rowid, title, body) 
    VALUES ('delete', OLD.id, OLD.title, OLD.body);
END;

CREATE TRIGGER IF NOT EXISTS trg_work_items_fts_update 
AFTER UPDATE ON work_items BEGIN
    INSERT INTO work_items_fts(work_items_fts, rowid, title, body) 
    VALUES ('delete', OLD.id, OLD.title, OLD.body);
    INSERT INTO work_items_fts(rowid, title, body) 
    VALUES (NEW.id, NEW.title, NEW.body);
END;
```

---

## 4. Views для UI-слоя

Эти представления упрощают запросы из Python/GTK и отделяют логику отображения от хранения.

```sql
-- -----------------------------------------------------------
-- DASHBOARD: Мои обязательства (я кому-то обещал)
-- -----------------------------------------------------------
CREATE VIEW IF NOT EXISTS v_my_commitments AS
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
WHERE p_me.is_me = 1 AND c.status = 'active';

-- -----------------------------------------------------------
-- DASHBOARD: Их обязательства мне
-- -----------------------------------------------------------
CREATE VIEW IF NOT EXISTS v_their_commitments AS
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
WHERE p_me.is_me = 1 AND c.status = 'active';

-- -----------------------------------------------------------
-- TODAY: Матрица Эйзенхауера
-- -----------------------------------------------------------
CREATE VIEW IF NOT EXISTS v_today_matrix AS
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
    due_date ASC;

-- -----------------------------------------------------------
-- PORTFOLIO: Здоровье проектов с бюджетом
-- -----------------------------------------------------------
CREATE VIEW IF NOT EXISTS v_project_portfolio AS
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
WHERE p.status != 'cancelled';

-- -----------------------------------------------------------
-- BUDGET: Факт по статьям с остатками
-- -----------------------------------------------------------
CREATE VIEW IF NOT EXISTS v_budget_status AS
SELECT 
    bl.id,
    bl.name,
    bl.type,
    bl.annual_plan,
    COALESCE(SUM(CASE WHEN be.entry_type = 'fact' THEN be.amount ELSE 0 END), 0) AS total_fact,
    bl.annual_plan - COALESCE(SUM(CASE WHEN be.entry_type = 'fact' THEN be.amount ELSE 0 END), 0) AS remaining
FROM budget_lines bl
LEFT JOIN budget_entries be ON bl.id = be.budget_line_id
GROUP BY bl.id;
```

---

## 5. Ключевые запросы для экранов

### Dashboard: «Ситуация» (Python-псевдокод)

```sql
-- KPI Health
SELECT title, kpi_current, kpi_target, kpi_unit, status 
FROM goals 
WHERE status IN ('active', 'at_risk') 
ORDER BY sort_order;

-- Мои обязательства на сегодня
SELECT * FROM v_my_commitments 
WHERE urgency_flag IN ('today', 'overdue') 
ORDER BY due_date;

-- Их обязательства мне — горят
SELECT * FROM v_their_commitments 
WHERE urgency_flag IN ('today', 'overdue') 
ORDER BY due_date;

-- Inbox count
SELECT COUNT(*) FROM work_items WHERE status = 'inbox' AND deleted_at IS NULL;
```

### Today: Эйзенхауер

```sql
-- Важно + Срочно (делаю сам)
SELECT * FROM v_today_matrix WHERE quadrant = 'do';

-- Важно, не срочно (планирую)
SELECT * FROM v_today_matrix WHERE quadrant = 'schedule' AND due_date IS NULL;

-- Срочно, не важно (делегирую)
SELECT * FROM v_today_matrix WHERE quadrant = 'delegate';
```

### Портфель: Квартальный таймлайн

```sql
SELECT * FROM v_project_portfolio 
WHERE quarter_label = '2026-Q2'
ORDER BY 
    CASE health 
        WHEN 'red' THEN 1 
        WHEN 'yellow' THEN 2 
        WHEN 'green' THEN 3 
        ELSE 4 
    END;
```

### Карточка человека

```sql
-- Все обязательства с этим человеком
SELECT c.*, 
    CASE WHEN p_from.is_me = 1 THEN 'outgoing' ELSE 'incoming' END AS direction
FROM commitments c
JOIN people p_from ON c.from_person_id = p_from.id
JOIN people p_to ON c.to_person_id = p_to.id
WHERE (p_from.id = ? OR p_to.id = ?) AND c.status = 'active'
ORDER BY c.due_date;

-- История встреч
SELECT m.*, group_concat(p.name, ', ') AS attendees
FROM meetings m
JOIN meeting_attendees ma ON m.id = ma.meeting_id
JOIN people p ON ma.person_id = p.id
WHERE m.id IN (
    SELECT meeting_id FROM meeting_attendees WHERE person_id = ?
)
GROUP BY m.id
ORDER BY m.meeting_date DESC;

-- Заметки о человеке
SELECT * FROM meeting_notes WHERE person_id = ? ORDER BY created_at DESC;
```

---

## 6. Python Data Access Layer (минимальный)

Поскольку GTK4 + libadwaita, рекомендую **чистый `sqlite3`** (входит в stdlib) + **dataclasses**. Это избавляет от зависимостей и проблем с потоками.

```python
# automata/db.py
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List


@dataclass
class Commitment:
    id: Optional[int]
    work_item_id: Optional[int]
    from_person_id: int
    to_person_id: int
    title: str
    promised_date: Optional[str]
    due_date: str
    status: str
    notes: Optional[str]
    urgency_flag: Optional[str] = None  # из view


class Database:
    SCHEMA_VERSION = 1
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()
    
    def _init_schema(self):
        """Проверка версии и накат миграций"""
        cur = self.conn.execute(
            "SELECT COALESCE(MAX(version), 0) FROM schema_version"
        )
        current = cur.fetchone()[0]
        
        if current < self.SCHEMA_VERSION:
            self._migrate(current)
    
    def _migrate(self, from_version: int):
        if from_version == 0:
            with open("schema.sql", "r") as f:
                self.conn.executescript(f.read())
            self.conn.execute(
                "INSERT INTO schema_version(version) VALUES (?)",
                (self.SCHEMA_VERSION,)
            )
            self.conn.commit()
    
    # --- Commitments API ---
    
    def create_commitment(
        self, 
        from_person_id: int,
        to_person_id: int,
        title: str,
        due_date: str,
        work_item_id: Optional[int] = None,
        promised_date: Optional[str] = None,
        notes: Optional[str] = None
    ) -> int:
        cur = self.conn.execute("""
            INSERT INTO commitments 
                (work_item_id, from_person_id, to_person_id, title, 
                 promised_date, due_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (work_item_id, from_person_id, to_person_id, title,
              promised_date, due_date, notes))
        self.conn.commit()
        return cur.lastrowid
    
    def get_my_commitments(self, status: str = 'active') -> List[Commitment]:
        """Использует view v_my_commitments"""
        rows = self.conn.execute("""
            SELECT * FROM v_my_commitments 
            WHERE status = ? 
            ORDER BY urgency_flag, due_date
        """, (status,)).fetchall()
        return [Commitment(**dict(r)) for r in rows]
    
    def fulfill_commitment(self, commitment_id: int):
        self.conn.execute("""
            UPDATE commitments 
            SET status = 'fulfilled', fulfillment_date = datetime('now')
            WHERE id = ?
        """, (commitment_id,))
        self.conn.commit()
    
    def breach_commitment(self, commitment_id: int, reason: Optional[str] = None):
        self.conn.execute("""
            UPDATE commitments 
            SET status = 'breached', notes = COALESCE(notes, '') || '\nBreached: ' || ?
            WHERE id = ?
        """, (reason or datetime.now().isoformat(), commitment_id))
        self.conn.commit()
    
    # --- Work Items API ---
    
    def inbox_count(self) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) FROM work_items WHERE status = 'inbox' AND deleted_at IS NULL"
        ).fetchone()
        return row[0]
    
    def quick_capture(self, title: str, item_type: str = 'task') -> int:
        """Ctrl+Space — мгновенный захват"""
        cur = self.conn.execute("""
            INSERT INTO work_items (type, title, status) VALUES (?, ?, 'inbox')
        """, (item_type, title))
        self.conn.commit()
        return cur.lastrowid
    
    def process_inbox_item(
        self, 
        item_id: int,
        action: str,  # 'do', 'schedule', 'delegate', 'archive', 'link_project'
        **kwargs
    ):
        """Обработка входящего элемента по методу GTD+Эйзенхауер"""
        if action == 'do':
            self.conn.execute("""
                UPDATE work_items 
                SET status = 'todo', urgency = 1, importance = 1 
                WHERE id = ?
            """, (item_id,))
        elif action == 'delegate':
            # Создаём commitment автоматически
            self.conn.execute("""
                UPDATE work_items 
                SET status = 'delegated', urgency = 1, importance = 0 
                WHERE id = ?
            """, (item_id,))
            if 'to_person_id' in kwargs and 'due_date' in kwargs:
                self.create_commitment(
                    from_person_id=kwargs['to_person_id'],
                    to_person_id=kwargs.get('my_person_id', 1),
                    title=kwargs.get('commitment_title', 'Delegated task'),
                    due_date=kwargs['due_date'],
                    work_item_id=item_id
                )
        elif action == 'schedule':
            self.conn.execute("""
                UPDATE work_items 
                SET status = 'scheduled', scheduled_date = ? 
                WHERE id = ?
            """, (kwargs.get('date'), item_id))
        elif action == 'archive':
            self.conn.execute("""
                UPDATE work_items SET status = 'archived' WHERE id = ?
            """, (item_id,))
        self.conn.commit()
    
    # --- Search ---
    
    def search(self, query: str) -> List[sqlite3.Row]:
        """FTS5 по work_items"""
        return self.conn.execute("""
            SELECT w.* FROM work_items w
            JOIN work_items_fts fts ON w.id = fts.rowid
            WHERE work_items_fts MATCH ?
            ORDER BY rank
        """, (query,)).fetchall()
    
    def close(self):
        self.conn.close()
```

---

## 7. Миграции и версионирование

Поскольку это local-first приложение, миграции проще, чем в вебе. Алгоритм:

```python
# В Database._migrate()
MIGRATIONS = {
    1: "schema_v1.sql",
    2: "migrations/v2_add_email_threads.sql",
    3: "migrations/v3_add_kpi_history.sql",
}

def _migrate(self, current: int):
    for version in range(current + 1, self.SCHEMA_VERSION + 1):
        if version in MIGRATIONS:
            with open(MIGRATIONS[version]) as f:
                self.conn.executescript(f.read())
            self.conn.execute(
                "INSERT INTO schema_version(version) VALUES (?)", (version,)
            )
            self.conn.commit()
```

**Правило:** Никогда не изменяйте существующие `schema_vN.sql`. Только добавляйте новые миграции.

---

## 8. Расширяемость (на будущее)

| Фича | Как добавить без переписывания |
|------|-------------------------------|
| **Кастомные поля** | Таблица `custom_fields(definition_json)` + `item_custom_values(item_id, field_id, value)` |
| **Синхронизация** | Добавить `uuid TEXT UNIQUE` ко всем таблицам + `sync_state` (local/remote/conflict) |
| **AI-эмбеддинги** | Таблица `embeddings(item_id, vector BLOB)` + поиск через sqlite-vec |
| **Шифрование** | SQLCipher вместо SQLite (прозрачно для приложения) |
| **Time-tracking** | Таблица `time_entries(work_item_id, started_at, ended_at)` |
