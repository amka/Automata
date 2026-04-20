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
from automata.services.project_service import project_service


class ProjectItem(GObject.GObject):
    __gtype_name__ = "ProjectItem"

    def __init__(self, project: Project):
        super().__init__()
        self.project = project


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/projects_page.ui")
class ProjectsPage(Gtk.Box):
    __gtype_name__ = "ProjectsPage"

    list_view: Gtk.ListView = Gtk.Template.Child()
    selection_model: Gtk.SingleSelection = Gtk.Template.Child()

    projects_store: Gio.ListStore

    def __init__(self):
        super().__init__()

        self.projects_store = Gio.ListStore(item_type=ProjectItem)
        self.selection_model.set_model(
            Gtk.SortListModel(
                model=self.projects_store,
                # sorter=...,  # можно добавить Gtk.CustomSorter
            )
        )

        # self._load_projects()

    def populate(self):
        self._load_projects()

    @Gtk.Template.Callback()
    def _setup_list_row(self, factory, item):
        row = Adw.ActionRow()
        row.set_subtitle_selectable(True)
        # Меню (правый клик или кнопка)
        menu = Gio.Menu()
        menu.append("Редактировать", "app.edit_project")
        menu.append("Удалить", "app.delete_project")
        menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu)
        row.add_suffix(menu_button)

        item.set_child(row)

    @Gtk.Template.Callback()
    def _bind_list_row(self, factory, item):
        project: ProjectItem = item.get_item()
        row: Adw.ActionRow = item.get_child()
        if not project:
            return
        row.set_title(f"{project.project.name}")
        row.set_subtitle(
            f"Дедлайн: {project.project.target_date or '—'} | Прогресс: {project.project.progress}%"
        )
        # Можно добавить статус-иконку

    def _load_projects(self):
        def worker():
            projects = project_service.get_all_projects()
            GLib.idle_add(self._update_list_ui, projects)

        threading.Thread(target=worker, daemon=True).start()

    def _update_list_ui(self, projects: List[Project]):
        self.projects_store.remove_all()
        for p in projects:
            self.projects_store.append(ProjectItem(p))
        logger.debug(f"Loaded {len(projects)} projects")
        return False

    @Gtk.Template.Callback()
    def _on_project_selected(self, selection, position, n_items):
        if n_items == 0:
            return
        project = selection.get_selected_item()
        if project:
            detail_page = self._create_detail_page(project)
            self.push(detail_page)

    def _create_detail_page(self, project: Project) -> Adw.NavigationPage:
        # Здесь будет детальная карточка + список задач проекта
        # (можно сделать Adw.NavigationPage с HeaderBar + ScrolledWindow)
        # Пока заглушка — потом расширим
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle(title=f"{project.name}", subtitle=""))
        box.append(header)

        # TODO: добавить прогресс, описание, кнопки JIRA/GitLab
        # + список задач (отдельный ListView с TaskService)

        return Adw.NavigationPage(title=f"{project.name}", child=box)

    def _show_create_dialog(self, btn):
        # Здесь можно открыть Adw.MessageDialog или отдельный dialog для создания
        # После создания — self._load_projects()
        pass
