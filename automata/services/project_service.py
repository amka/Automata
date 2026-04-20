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
from typing import List

from gi.repository import GObject

from automata.core.models import Project, Task


class ProjectSignal(enum.Enum):
    ITEM_ADDED = "item-added"
    ITEM_REMOVED = "item-removed"
    ITEM_UPDATED = "item-updated"


class ProjectService(GObject.GObject):
    __gtype_name__ = "ProjectService"

    __gsignals__ = {
        ProjectSignal.ITEM_ADDED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
        ProjectSignal.ITEM_REMOVED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
        ProjectSignal.ITEM_UPDATED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
    }

    def get_all_projects(self) -> List[Project]:
        """Дефолтная сортировка: order_index + target_date"""
        return list(Project.select().order_by(Project.order_index, Project.target_date))

    def get_project_by_id(self, project_id: int) -> Project | None:
        return Project.get_or_none(Project.id == project_id)

    def create_project(self, **kwargs) -> Project:
        project = Project.create(**kwargs)
        self.emit(ProjectSignal.ITEM_ADDED.value, project)
        return project

    def update_project(self, project_id: int, **kwargs) -> Project | None:
        project = Project.get_or_none(Project.id == project_id)
        if project:
            for key, value in kwargs.items():
                setattr(project, key, value)
            project.save()
            self.emit(ProjectSignal.ITEM_UPDATED.value, project)
        return project

    def delete_project(self, project_id: int) -> bool:
        project = Project.get_or_none(Project.id == project_id)
        if project:
            project.delete_instance(recursive=True)  # удалит и все связанные задачи
            self.emit(ProjectSignal.ITEM_REMOVED.value, project)
            return True
        return False

    def update_order(self, projects_order: List[int]):
        """projects_order — список id в новом порядке"""
        for index, pid in enumerate(projects_order):
            Project.update(order_index=index).where(Project.id == pid).execute()

    def get_project_tasks(self, project_id: int) -> List[Task]:
        return list(
            Task.select().where(Task.project == project_id).order_by(Task.due_date)
        )


# Due to need to notify observers, we use a singleton
project_service = ProjectService()
