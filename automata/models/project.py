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
from imaplib import Commands
from typing import List


# -- 1. Projects (высокоуровневые инициативы, которые ты контролируешь)
# CREATE TABLE projects (
#     id              INTEGER PRIMARY KEY AUTOINCREMENT,
#     name            TEXT NOT NULL,
#     description     TEXT,
#     status          TEXT DEFAULT 'active' CHECK(status IN ('active', 'on_hold', 'completed', 'cancelled')),
#     priority        INTEGER DEFAULT 3,                    -- 1=highest, 4=lowest
#     start_date      DATE,
#     target_date     DATE,
#     completed_at    TIMESTAMP,
#     progress        REAL DEFAULT 0.0,                     -- 0-100, рассчитывается или вручную
#     jira_board_key  TEXT,                                 -- например, "PROJ-123"
#     gitlab_group_id TEXT,
#     grafana_dashboard_url TEXT,
#     created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
@dataclass
class Project:
    id: int | None = None
    name: str = ""
    description: str | None = None
    status: str = "active"  # 'active', 'on_hold', 'completed', 'cancelled'
    priority: int = 3  # 1=highest, 4=lowest
    start_date: str | None = None
    target_date: str | None = None
    completed_at: str | None = None
    progress: float = 0.0  # 0-100, рассчитывается или вручную
    jira_board_key: str | None = None  # "PROJ-123"
    gitlab_group_id: str | None = None
    grafana_dashboard_url: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
