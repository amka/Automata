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
from typing import List, Optional

from gi.repository import GObject

from automata.core.models import Goal, db


class GoalSignal(enum.Enum):
    GOAL_ADDED = "goal-added"
    GOAL_UPDATED = "goal-updated"
    GOAL_DELETED = "goal-deleted"


class GoalService(GObject.GObject):
    __gtype_name__ = "GoalService"
    __gsignals__ = {
        GoalSignal.GOAL_ADDED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
        GoalSignal.GOAL_UPDATED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
        GoalSignal.GOAL_DELETED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
    }

    def __init__(self):
        super().__init__()

    def get_all_goals(
        self, year: Optional[int] = None, status: Optional[str] = None
    ) -> List[Goal]:
        query = Goal.select()
        if year:
            query = query.where(Goal.year == year)
        if status:
            query = query.where(Goal.status == status)
        return list(query.order_by(Goal.created_at.desc()))

    def get_goal_by_id(self, goal_id: int) -> Optional[Goal]:
        return Goal.get_or_none(Goal.id == goal_id)

    def get_active_goals(self, year: Optional[int] = None) -> List[Goal]:
        query = Goal.select().where(Goal.status == "active")
        if year:
            query = query.where(Goal.year == year)
        return list(query.order_by(Goal.created_at.desc()))

    def create_goal(self, **kwargs) -> Goal:
        with db.atomic():
            result = Goal.create(**kwargs)
            self.emit(GoalSignal.GOAL_ADDED.value, result)
            return result

    def update_goal(self, goal_id: int, **kwargs) -> Optional[Goal]:
        goal = Goal.get_or_none(Goal.id == goal_id)
        if goal:
            for key, value in kwargs.items():
                if hasattr(goal, key):
                    setattr(goal, key, value)
            goal.save()
            self.emit(GoalSignal.GOAL_UPDATED.value, goal)
        return goal

    def delete_goal(self, goal_id: int) -> bool:
        goal = Goal.get_or_none(Goal.id == goal_id)
        if goal:
            goal.delete_instance(recursive=True)
            self.emit(GoalSignal.GOAL_DELETED.value, goal)
            return True
        return False

    def update_progress(self, goal_id: int, current_value: float) -> Optional[Goal]:
        goal = Goal.get_or_none(Goal.id == goal_id)
        if goal:
            goal.current_value = current_value
            if goal.target_value and goal.current_value >= goal.target_value:
                goal.status = "completed"
            goal.save()
        return goal

    def get_goals_with_okrs(self, year: Optional[int] = None) -> List[Goal]:
        query = Goal.select().where(Goal.status == "active")
        if year:
            query = query.where(Goal.year == year)
        return list(query.prefetch(Goal.okrs))


goal_service = GoalService()
