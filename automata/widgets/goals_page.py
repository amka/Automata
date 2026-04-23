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

import threading
from typing import List

from gi.repository import Adw, Gio, GLib, GObject, Gtk
from loguru import logger

from automata.core.models import Goal
from automata.services import goal_service
from automata.services.goal_service import GoalSignal


class GoalItem(GObject.GObject):
    __gtype_name__ = "GoalItem"

    goal: Goal = GObject.Property(type=GObject.TYPE_PYOBJECT)

    def __init__(self, goal: Goal):
        super().__init__()
        self.goal = goal


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/goals_page.ui")
class GoalsPage(Adw.NavigationPage):
    __gtype_name__ = "GoalsPage"

    list_view: Gtk.ListView = Gtk.Template.Child()
    selection_model: Gtk.SingleSelection = Gtk.Template.Child()

    goals_store: Gio.ListStore

    def __init__(self):
        super().__init__()

        # Инициализация store
        self.goals_store = Gio.ListStore(item_type=GoalItem)

        sorted_model = Gtk.SortListModel(model=self.goals_store)
        # Позже можно добавить кастомный sorter по order_index + target_date
        self.selection_model.set_model(sorted_model)

        self.connect_signals()

    def connect_signals(self):
        # Подключаем сигналы
        self.selection_model.connect("selection-changed", self._on_goal_selected)

        # Следим за изменениями в проектах
        goal_service.connect(GoalSignal.GOAL_ADDED.value, self._on_goal_added)
        # goal_service.connect(GoalSignal.GOAL_UPDATED.value, self._on_goal_updated)
        # goal_service.connect(GoalSignal.GOAL_DELETED.value, self._on_goal_removed)

    def populate(self):
        self._load_goals()

    @Gtk.Template.Callback()
    def _setup_list_row(self, _factory: Gtk.ListItemFactory, list_item: Gtk.ListItem):
        row = Adw.ActionRow()
        row.set_subtitle_selectable(True)

        # Меню действий
        menu = Gio.Menu()
        menu.append("Редактировать", "app.goal.edit")
        menu.append("Удалить", "app.goal.delete")

        menu_button = Gtk.MenuButton(
            icon_name="open-menu-symbolic", menu_model=menu, valign=Gtk.Align.CENTER
        )
        row.add_suffix(menu_button)

        list_item.set_child(row)

    @Gtk.Template.Callback()
    def _bind_list_row(self, _factory: Gtk.ListItemFactory, list_item: Gtk.ListItem):
        goal_item: GoalItem = list_item.get_item()
        if not goal_item or not goal_item.goal:
            return

        row: Adw.ActionRow = list_item.get_child()
        g: Goal = goal_item.goal

        row.set_title(f"{g.title}")
        row.set_subtitle(f"Дедлайн: {g.year or '—'} • Прогресс: {g.progress:.0f}%")

        # Можно добавить префикс-иконку по статусу
        # if p.status == "completed": row.set_icon_name("emblem-ok-symbolic")

    def _load_goals(self):
        def worker():
            try:
                goals = goal_service.get_active_goals()
                GLib.idle_add(self._update_list_ui, goals)
            except Exception as e:
                logger.error(f"Failed to load goals: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def _update_list_ui(self, goals: List[Goal]):
        self.goals_store.remove_all()
        for g in goals:
            self.goals_store.append(GoalItem(g))
        logger.info(f"Loaded {len(goals)} goals into UI")
        return False

    @Gtk.Template.Callback()
    def _on_goal_selected(
        self, selection: Gtk.SingleSelection, position: int, n_items: int
    ):
        if n_items == 0:
            return

        goal_item: GoalItem = selection.get_selected_item()
        if not goal_item:
            return

        logger.debug(f"Goal selected: {goal_item.goal}")

        # detail_page = self._create_detail_page(goal_item.goal)
        # self.get_navigation_view().push(detail_page)  # ← правильная навигация

    # def _create_detail_page(self, goal: Goal) -> Adw.NavigationPage:
    #     # Пока простая заглушка. Следующим шагом сделаем полноценную страницу
    #     content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

    #     header = Adw.HeaderBar()
    #     header.set_title_widget(
    #         Adw.WindowTitle(title=project.name, subtitle=f"ID: {project.id}")
    #     )
    #     content.append(header)

    #     # Прогресс
    #     progress_row = Adw.ActionRow(title="Прогресс")
    #     progress_bar = Gtk.ProgressBar(fraction=project.progress / 100.0)
    #     progress_row.add_suffix(progress_bar)
    #     content.append(progress_row)

    #     # Описание
    #     if project.description:
    #         desc_label = Gtk.Label(label=project.description, wrap=True, xalign=0)
    #         content.append(desc_label)

    #     # TODO: список задач проекта + ссылки на JIRA/GitLab

    #     return Adw.NavigationPage(title=project.name, child=content)

    def _on_goal_added(self, sender, goal: Goal) -> None:
        logger.debug(f"Goal added: {goal}")
        self.goals_store.append(GoalItem(goal))
