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

from datetime import date, datetime
from typing import List, Optional

from automata.core.models import Task, db


class TaskService:
    @staticmethod
    async def create_task(**kwargs) -> Task:
        with db.atomic():  # транзакция
            return Task.create(**kwargs)

    @staticmethod
    def quick_create(
        title: str,
        description: Optional[str] = None,
        due_date: Optional[date] = None,
        priority: int = 3,
        project_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        eisenhower: Optional[str] = None,
        **kwargs,
    ) -> Task:
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        params = dict(
            title=title.strip(),
            description=description,
            due_date=due_date,
            priority=priority,
            project_id=project_id,
            tags=tags or [],
            eisenhower=eisenhower,
            status="todo",
        )
        params.update(kwargs)

        with db.atomic():  # транзакция
            return Task.create(**params)

    @staticmethod
    def get_today_tasks() -> List[Task]:
        return list(Task.select().where(Task.due_date == date.today()))

    @staticmethod
    def get_inbox_tasks() -> List[Task]:
        """Задачи без due_date или с ближайшими датами, которые ещё не обработаны"""
        return list(
            Task.select().where(Task.status == "todo").order_by(Task.created_at)
        )

    @staticmethod
    async def get_task_by_id(task_id: int) -> Optional[Task]:
        try:
            return await Task.get(id=task_id).prefetch_related("project")
        except DoesNotExist:
            return None

    @staticmethod
    async def update_status(task_id: int, new_status: str) -> Optional[Task]:
        task = await TaskService.get_task_by_id(task_id)
        if task:
            task.status = new_status
            if new_status == "done":
                task.completed_at = datetime.now()
            await task.save()
        return task
