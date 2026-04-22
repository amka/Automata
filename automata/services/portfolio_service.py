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

from typing import List, Optional

from automata.core.models import Project, Task, db


class PortfolioService:
    @staticmethod
    def get_all_projects(
        okr_id: Optional[int] = None,
        goal_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Project]:
        query = Project.select()
        if okr_id:
            query = query.where(Project.okr == okr_id)
        if goal_id:
            query = query.where(Project.goal == goal_id)
        if status:
            query = query.where(Project.status == status)
        return list(query.order_by(Project.created_at.desc()))

    @staticmethod
    def get_project_by_id(project_id: int) -> Optional[Project]:
        return Project.get_or_none(Project.id == project_id)

    @staticmethod
    def get_active_projects() -> List[Project]:
        return list(
            Project.select()
            .where(Project.status.in_(["not_started", "in_progress", "at_risk"]))
            .order_by(Project.created_at.desc())
        )

    @staticmethod
    def create_project(**kwargs) -> Project:
        with db.atomic():
            return Project.create(**kwargs)

    @staticmethod
    def update_project(project_id: int, **kwargs) -> Optional[Project]:
        project = Project.get_or_none(Project.id == project_id)
        if project:
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            project.save()
        return project

    @staticmethod
    def delete_project(project_id: int) -> bool:
        project = Project.get_or_none(Project.id == project_id)
        if project:
            project.delete_instance(recursive=True)
            return True
        return False

    @staticmethod
    def get_project_tasks(project_id: int) -> List[Task]:
        return list(
            Task.select()
            .where(Task.project == project_id)
            .order_by(Task.due_date, Task.priority.desc())
        )

    @staticmethod
    def get_projects_by_owner(owner: str) -> List[Project]:
        return list(Project.select().where(Project.owner == owner))

    @staticmethod
    def get_projects_summary(
        okr_id: Optional[int] = None, goal_id: Optional[int] = None
    ) -> dict:
        projects = PortfolioService.get_all_projects(okr_id=okr_id, goal_id=goal_id)
        total = len(projects)
        completed = sum(1 for p in projects if p.status == "completed")
        in_progress = sum(1 for p in projects if p.status == "in_progress")
        at_risk = sum(1 for p in projects if p.status == "at_risk")

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "at_risk": at_risk,
            "not_started": total - completed - in_progress - at_risk,
        }


portfolio_service = PortfolioService()