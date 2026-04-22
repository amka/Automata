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

from automata.core.models import BudgetEntry, db


class BudgetService:
    @staticmethod
    def get_all_entries(
        goal_id: Optional[int] = None,
        okr_id: Optional[int] = None,
        project_id: Optional[int] = None,
        task_id: Optional[int] = None,
        category: Optional[str] = None,
    ) -> List[BudgetEntry]:
        query = BudgetEntry.select()
        if goal_id:
            query = query.where(BudgetEntry.goal == goal_id)
        if okr_id:
            query = query.where(BudgetEntry.okr == okr_id)
        if project_id:
            query = query.where(BudgetEntry.project == project_id)
        if task_id:
            query = query.where(BudgetEntry.task == task_id)
        if category:
            query = query.where(BudgetEntry.category == category)
        return list(query.order_by(BudgetEntry.created_at.desc()))

    @staticmethod
    def get_entry_by_id(entry_id: int) -> Optional[BudgetEntry]:
        return BudgetEntry.get_or_none(BudgetEntry.id == entry_id)

    @staticmethod
    def create_entry(**kwargs) -> BudgetEntry:
        with db.atomic():
            return BudgetEntry.create(**kwargs)

    @staticmethod
    def update_entry(entry_id: int, **kwargs) -> Optional[BudgetEntry]:
        entry = BudgetEntry.get_or_none(BudgetEntry.id == entry_id)
        if entry:
            for key, value in kwargs.items():
                if hasattr(entry, key):
                    setattr(entry, key, value)
            entry.save()
        return entry

    @staticmethod
    def delete_entry(entry_id: int) -> bool:
        entry = BudgetEntry.get_or_none(BudgetEntry.id == entry_id)
        if entry:
            entry.delete_instance()
            return True
        return False

    @staticmethod
    def record_spent(entry_id: int, amount: float) -> Optional[BudgetEntry]:
        entry = BudgetEntry.get_or_none(BudgetEntry.id == entry_id)
        if entry:
            entry.spent = entry.spent + amount
            entry.save()
        return entry

    @staticmethod
    def get_budget_summary(
        goal_id: Optional[int] = None,
        okr_id: Optional[int] = None,
        project_id: Optional[int] = None,
    ) -> dict:
        entries = BudgetService.get_all_entries(
            goal_id=goal_id, okr_id=okr_id, project_id=project_id
        )
        total_allocated = sum(e.allocated for e in entries)
        total_spent = sum(e.spent for e in entries)
        total_forecast = sum(e.forecast for e in entries)

        return {
            "allocated": total_allocated,
            "spent": total_spent,
            "forecast": total_forecast,
            "remaining": total_allocated - total_spent,
            "variance": total_allocated - total_forecast,
        }


budget_service = BudgetService()
