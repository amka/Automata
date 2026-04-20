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
from ast import Gt
from typing import List

from gi.repository import Adw, Gio, GLib, GObject, Gtk
from loguru import logger

from automata.core.models import Project
from automata.services.project_service import ProjectSignal, project_service


class ProjectItem(GObject.GObject):
    __gtype_name__ = "ProjectItem"

    project: Project = GObject.Property(type=GObject.TYPE_PYOBJECT)

    def __init__(self, project: Project):
        super().__init__()
        self.project = project


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/projects_page.ui")
class ProjectsPage(Adw.NavigationPage):
    __gtype_name__ = "ProjectsPage"

    list_view: Gtk.ListView = Gtk.Template.Child()
    selection_model: Gtk.SingleSelection = Gtk.Template.Child()

    projects_store: Gio.ListStore

    def __init__(self):
        super().__init__()

        # Инициализация store
        self.projects_store = Gio.ListStore(item_type=ProjectItem)

        sorted_model = Gtk.SortListModel(model=self.projects_store)
        # Позже можно добавить кастомный sorter по order_index + target_date
        self.selection_model.set_model(sorted_model)

        self.connect_signals()

    def connect_signals(self):
        # Подключаем сигналы
        self.selection_model.connect("selection-changed", self._on_project_selected)

        # Следим за изменениями в проектах
        project_service.connect(ProjectSignal.ITEM_ADDED.value, self._on_project_added)
        # project_service.connect(
        #     ProjectSignal.ITEM_UPDATED.value, self._on_project_updated
        # )
        # project_service.connect(
        #     ProjectSignal.ITEM_REMOVED.value, self._on_project_removed
        # )

    def populate(self):
        self._load_projects()

    @Gtk.Template.Callback()
    def _setup_list_row(self, factory: Gtk.ListItemFactory, list_item: Gtk.ListItem):
        row = Adw.ActionRow()
        row.set_subtitle_selectable(True)

        # Меню действий
        menu = Gio.Menu()
        menu.append("Редактировать", "app.project.edit")
        menu.append("Удалить", "app.project.delete")

        menu_button = Gtk.MenuButton(
            icon_name="open-menu-symbolic", menu_model=menu, valign=Gtk.Align.CENTER
        )
        row.add_suffix(menu_button)

        list_item.set_child(row)

    @Gtk.Template.Callback()
    def _bind_list_row(self, factory: Gtk.ListItemFactory, list_item: Gtk.ListItem):
        project_item: ProjectItem = list_item.get_item()
        if not project_item or not project_item.project:
            return

        row: Adw.ActionRow = list_item.get_child()
        p: Project = project_item.project

        row.set_title(f"{p.name}")
        row.set_subtitle(
            f"Дедлайн: {p.target_date or '—'} • Прогресс: {p.progress:.0f}%"
        )

        # Можно добавить префикс-иконку по статусу
        # if p.status == "completed": row.set_icon_name("emblem-ok-symbolic")

    def _load_projects(self):
        def worker():
            try:
                projects = project_service.get_all_projects()
                GLib.idle_add(self._update_list_ui, projects)
            except Exception as e:
                logger.error(f"Failed to load projects: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def _update_list_ui(self, projects: List[Project]):
        self.projects_store.remove_all()
        for p in projects:
            self.projects_store.append(ProjectItem(p))
        logger.info(f"Loaded {len(projects)} projects into UI")
        return False

    @Gtk.Template.Callback()
    def _on_project_selected(
        self, selection: Gtk.SingleSelection, position: int, n_items: int
    ):
        if n_items == 0:
            return

        project_item: ProjectItem = selection.get_selected_item()
        if not project_item:
            return

        detail_page = self._create_detail_page(project_item.project)
        self.get_navigation_view().push(detail_page)  # ← правильная навигация

    def _create_detail_page(self, project: Project) -> Adw.NavigationPage:
        # Пока простая заглушка. Следующим шагом сделаем полноценную страницу
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        header = Adw.HeaderBar()
        header.set_title_widget(
            Adw.WindowTitle(title=project.name, subtitle=f"ID: {project.id}")
        )
        content.append(header)

        # Прогресс
        progress_row = Adw.ActionRow(title="Прогресс")
        progress_bar = Gtk.ProgressBar(fraction=project.progress / 100.0)
        progress_row.add_suffix(progress_bar)
        content.append(progress_row)

        # Описание
        if project.description:
            desc_label = Gtk.Label(label=project.description, wrap=True, xalign=0)
            content.append(desc_label)

        # TODO: список задач проекта + ссылки на JIRA/GitLab

        return Adw.NavigationPage(title=project.name, child=content)

    def _on_project_added(self, sender, project: Project) -> None:
        logger.debug(f"Project added: {project}")
        self.projects_store.append(ProjectItem(project))
