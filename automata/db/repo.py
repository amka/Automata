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

import json
from typing import List, Optional

from automata.models.task import Task

from .client import DatabaseClient


class TaskDAO:
    def __init__(self, db: DatabaseClient):
        self.db = db

    def _row_to_task(self, row) -> Task:
        return Task(
            id=row[0],
            title=row[1],
            description=row[2],
            quadrant=row[3],
            priority=row[4],
            due_date=row[5],
            tags=json.loads(row[6]) if row[6] else [],
            assignee=row[7],
            project_id=row[8],
            status=row[9],
            created_at=row[10],
            updated_at=row[11],
        )

    def create(self, task: Task) -> int:
        sql = """INSERT INTO tasks
                 (title, description, quadrant, priority, due_date, tags, assignee, project_id, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        params = (
            task.title,
            task.description,
            task.quadrant,
            task.priority,
            task.due_date,
            json.dumps(task.tags),
            task.assignee,
            task.project_id,
            task.status,
        )
        cur = self.db.execute(sql, params)
        self.db.commit()
        return cur.lastrowid

    def get_by_id(self, task_id: int) -> Optional[Task]:
        cur = self.db.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = cur.fetchone()
        return self._row_to_task(row) if row else None

    def get_all(
        self, quadrant: Optional[int] = None, status: str = "active", limit: int = 100
    ) -> List[Task]:
        sql = "SELECT * FROM tasks WHERE status=?"
        params: list = [status]
        if quadrant is not None:
            sql += " AND quadrant=?"
            params.append(quadrant)
        sql += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END, due_date ASC, created_at DESC LIMIT ?"
        params.append(limit)

        cur = self.db.execute(sql, tuple(params))
        return [self._row_to_task(r) for r in cur.fetchall()]

    def update(self, task: Task) -> bool:
        sql = """UPDATE tasks SET
                 title=?, description=?, quadrant=?, priority=?, due_date=?, tags=?, assignee=?, project_id=?, status=?, updated_at=datetime('now')
                 WHERE id=?"""
        params = (
            task.title,
            task.description,
            task.quadrant,
            task.priority,
            task.due_date,
            json.dumps(task.tags),
            task.assignee,
            task.project_id,
            task.status,
            task.id,
        )
        self.db.execute(sql, params)
        self.db.commit()
        return True

    def delete(self, task_id: int) -> bool:
        self.db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.db.commit()
        return True

    def bulk_move_quadrant(self, task_ids: List[int], quadrant: int):
        if not task_ids:
            return
        placeholders = ",".join("?" for _ in task_ids)
        sql = f"UPDATE tasks SET quadrant=?, updated_at=datetime('now') WHERE id IN ({placeholders})"
        self.db.execute(sql, [quadrant] + task_ids)
        self.db.commit()
