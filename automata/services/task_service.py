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

import enum
from datetime import date
from typing import List, Optional

from gi.repository import GObject

from automata.core.models import Task, db


class TaskSignal(enum.Enum):
    TASK_CREATED = "task-created"
    TASK_UPDATED = "task-updated"
    TASK_DELETED = "task-deleted"


class TaskService(GObject.GObject):
    __gtype_name__ = "TaskService"

    __gsignals__ = {
        TaskSignal.TASK_CREATED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
        TaskSignal.TASK_UPDATED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
        TaskSignal.TASK_DELETED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
    }

    def __init__(self):
        super().__init__()

    def get_all_tasks(
        self,
        project_id: Optional[int] = None,
        okr_id: Optional[int] = None,
        goal_id: Optional[int] = None,
        status: Optional[str] = None,
        assignee: Optional[str] = None,
        is_personal: Optional[bool] = None,
    ) -> List[Task]:
        query = Task.select()
        if project_id:
            query = query.where(Task.project == project_id)
        if okr_id:
            query = query.where(Task.okr == okr_id)
        if goal_id:
            query = query.where(Task.goal == goal_id)
        if status:
            query = query.where(Task.status == status)
        if assignee:
            query = query.where(Task.assignee == assignee)
        if is_personal is not None:
            query = query.where(Task.is_personal == is_personal)
        return list(query.order_by(Task.priority.desc(), Task.due_date))

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        return Task.get_or_none(Task.id == task_id)

    def create_task(self, **kwargs) -> Task:
        with db.atomic():
            result = Task.create(**kwargs)
            self.emit(TaskSignal.TASK_CREATED.value, result)
            return result

    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        task = Task.get_or_none(Task.id == task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.save()
            self.emit(TaskSignal.TASK_UPDATED.value, task)
        return task

    def delete_task(self, task_id: int) -> bool:
        task = Task.get_or_none(Task.id == task_id)
        if task:
            task.delete_instance()
            self.emit(TaskSignal.TASK_DELETED.value, task)
            return True
        return False

    def update_status(self, task_id: int, new_status: str) -> Optional[Task]:
        task = Task.get_or_none(Task.id == task_id)
        if task:
            task.status = new_status
            task.save()
            self.emit(TaskSignal.TASK_UPDATED.value, task)
        return task

    def get_tasks_by_due_date(self, due_date: date) -> List[Task]:
        return list(Task.select().where(Task.due_date == due_date))

    def get_overdue_tasks(self) -> List[Task]:
        return list(
            Task.select()
            .where((Task.due_date < date.today()) & (Task.status != "completed"))
            .order_by(Task.due_date)
        )

    def get_todays_tasks(self) -> List[Task]:
        return list(
            Task.select().where(
                (Task.due_date == date.today()) & (Task.status != "completed")
            )
        )

    def get_personal_tasks(self) -> List[Task]:
        return list(
            Task.select()
            .where(Task.is_personal)
            .order_by(Task.priority.desc(), Task.due_date)
        )

    def get_assigned_tasks(self, assignee: str) -> List[Task]:
        return list(
            Task.select()
            .where(Task.assignee == assignee)
            .order_by(Task.priority.desc(), Task.due_date)
        )


task_service = TaskService()
