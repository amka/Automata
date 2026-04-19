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

from tortoise import fields, models

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


class Note(models.Model):
    id = fields.IntField(pk=True)
    title = fields.TextField()
    start_time = fields.TextField(null=True)
    end_time = fields.TextField(null=True)
    description = fields.TextField(null=True)
    is_meeting = fields.BooleanField(null=True)
    notes = fields.TextField(null=True)
    extracted_task_ids = fields.JSONField(null=True)
    created_at = fields.TextField(null=True)
    updated_at = fields.TextField(null=True)
