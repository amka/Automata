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


# 4. Calendar Events (встречи + timeblocking)
# CREATE TABLE events (
#     id              INTEGER PRIMARY KEY AUTOINCREMENT,
#     title           TEXT NOT NULL,
#     start_time      TIMESTAMP NOT NULL,
#     end_time        TIMESTAMP NOT NULL,
#     description     TEXT,
#     is_meeting      BOOLEAN DEFAULT TRUE,
#     notes           TEXT,
#     extracted_task_ids TEXT,                              -- JSON array
#     created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
@dataclass
class Note:
    id: int | None = None
    title: str = ""
    start_time: str | None = None
    end_time: str | None = None
    description: str | None = None
    is_meeting: bool | None = None
    notes: str | None = None
    extracted_task_ids: list[int] | None = field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None
