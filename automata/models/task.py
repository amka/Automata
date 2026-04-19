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

from dataclasses import dataclass, field
from typing import List


# Task (ежедневные задачи + подзадачи проектов)
# CREATE TABLE tasks (
#     id              INTEGER PRIMARY KEY AUTOINCREMENT,
#     title           TEXT NOT NULL,
#     description     TEXT,
#     status          TEXT DEFAULT 'todo' CHECK(status IN ('todo', 'in_progress', 'done', 'blocked', 'cancelled')),
#     priority        INTEGER DEFAULT 3,                    -- 1-4
#     eisenhower      TEXT,                                 -- 'do', 'schedule', 'delegate', 'delete' (или NULL)
#     due_date        DATE,
#     start_date      DATE,
#     completed_at    TIMESTAMP,
#     time_estimate   INTEGER,                              -- минут
#     time_spent      INTEGER DEFAULT 0,                    -- минут
#     project_id      INTEGER REFERENCES projects(id) ON DELETE SET NULL,
#     parent_task_id  INTEGER REFERENCES tasks(id) ON DELETE CASCADE,  -- для подзадач
#     is_recurring    BOOLEAN DEFAULT FALSE,
#     recurrence_rule TEXT,                                 -- например, "FREQ=WEEKLY;BYDAY=MO"
#     jira_key        TEXT,                                 -- "PROJ-456"
#     incident_id     TEXT,                                 -- из вашей кастомной системы
#     tags            TEXT,                                 -- JSON array: ["strategy", "ops", "team1"]
#     created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
@dataclass
class Task:
    id: int | None = None
    title: str = ""
    description: str | None = None
    status: str = "todo"  # 'todo', 'in_progress', 'done', 'blocked', 'cancelled'
    priority: int = 3  # 1=highest, 4=lowest
    eisenhower: str | None = None  # 'do', 'schedule', 'delegate', 'delete' (или NULL)
    due_date: str | None = None
    start_date: str | None = None
    completed_at: str | None = None
    assignee: str | None = None
    project_id: int | None = None
    parent_task_id: int | None = None
    time_estimate: int | None = None
    time_spent: int = 0
    is_recurring: bool = False
    recurrence_rule: str | None = None
    jira_key: str | None = None
    incident_id: str | None = None
    tags: List[str] = field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None
