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

from dataclasses import dataclass

# 5. Tags (для удобного поиска)
# CREATE TABLE tags (
#     id              INTEGER PRIMARY KEY AUTOINCREMENT,
#     name            TEXT UNIQUE NOT NULL,
#     color           TEXT DEFAULT '#3584e4'                -- hex для отображения
# );


# CREATE TABLE task_tags (
#     task_id         INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
#     tag_id          INTEGER REFERENCES tags(id) ON DELETE CASCADE,
#     PRIMARY KEY (task_id, tag_id)
# );
@dataclass
class Tag:
    id: int | None = None
    name: str = ""
    color: str | None = None


@dataclass
class TaskTag:
    task_id: int | None = None
    tag_id: int | None = None
