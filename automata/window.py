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

from ast import Gt
from typing import Dict

from gi.repository import Adw, Gio, Gtk
from loguru import logger

from automata.widgets.dashboard import DashboardPage
from automata.widgets.goals_page import GoalsPage
from automata.widgets.inbox import InboxPage
from automata.widgets.projects_page import ProjectsPage
from automata.widgets.quick_capture import QuickAddDialog
from automata.widgets.setup_wizard import SetupWizard


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/window.ui")
class AutomataWindow(Adw.ApplicationWindow):
    __gtype_name__ = "AutomataWindow"

    shortcut_controller: Gtk.ShortcutController = Gtk.Template.Child()
    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()
    screens: Gtk.Stack = Gtk.Template.Child()
    split_view: Adw.OverlaySplitView = Gtk.Template.Child()
    sidebar_page: Adw.NavigationPage = Gtk.Template.Child()
    sidebar: Gtk.ListBox = Gtk.Template.Child()
    content_page: Adw.NavigationPage = Gtk.Template.Child()
    view_stack: Gtk.Stack = Gtk.Template.Child()
    # pages_view: Adw.NavigationView = Gtk.Template.Child()

    settings: Gio.Settings

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Хранилище UI-состояния
        self.task_widgets: Dict[int, Gtk.ListBoxRow] = {}

        self._build_ui()
        self._setup_shortcuts()
        self._connect_signals()
        # self._load_view("today")

        # Init shortcut controller
        trigger = Gtk.ShortcutTrigger.parse_string("<Primary>k")
        action = Gtk.CallbackAction.new(lambda *args: self.show_quick_add())
        shortcut = Gtk.Shortcut.new(trigger, action)
        self.shortcut_controller.add_shortcut(shortcut)

        self._bind_settings()

    @Gtk.Template.Callback()
    def _on_begin_btn_clicked(self, _widget: Gtk.Widget):
        wizard = SetupWizard()
        # wizard.set_parent(self)
        wizard.present(self)

    def show_quick_add(self):
        logger.info("Show quick add dialog")
        dlg = QuickAddDialog()
        dlg.present(self)

    def _bind_settings(self):
        self.settings = Gio.Settings(schema_id="com.tenderowl.automata")
        self.settings.bind(
            "width", self, "default-width", Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "height", self, "default-height", Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "is-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT
        )
        self.settings.bind(
            "is-fullscreen", self, "fullscreened", Gio.SettingsBindFlags.DEFAULT
        )

    def _connect_signals(self):
        self.sidebar.connect("row-activated", self._on_sidebar_activated)

    def show_toast(self, message: str):
        toast = Adw.Toast.new(message)
        self.toast_overlay.add_toast(toast)

    def _build_ui(self):
        # Populate sidebar
        views = [
            ("pulse", "Pulse", "Dashboard"),
            ("strategy", "Strategy", "Year + Quarter"),
            ("portfolio", "Portfolio", "Projects"),
            ("me", "Me", "Personal + Inbox"),
            ("budget", "Budget", "Tasks"),
            ("reports", "Reports", "Reports"),
        ]
        for view_id, title, desc in views:
            row = Adw.ActionRow(title=title, subtitle=desc)
            row.set_activatable(True)
            row.view_id = view_id
            self.sidebar.append(row)

        # CONTENT
        dashboard = DashboardPage()
        dashboard.view_id = "pulse"
        self.view_stack.add_titled(dashboard, "pulse", "Dashboard")
        # self.pages_view.add(dashboard)

        strategy_page = GoalsPage()
        strategy_page.view_id = "strategy"
        self.view_stack.add_titled(strategy_page, "strategy", "Strategy")
        # self.pages_view.add(strategy_page)

        projects_view = ProjectsPage()
        self.view_stack.add_titled(projects_view, "projects", "Projects")
        # self.pages_view.add(projects_view)

        # Создаём страницы-списки
        for view_id in ["portfolio", "me", "budget"]:
            page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            page.set_spacing(8)
            page.set_margin_start(12)
            page.set_margin_end(12)
            page.set_margin_top(8)
            page.set_margin_bottom(8)

            task_list = Gtk.ListBox()
            task_list.set_selection_mode(Gtk.SelectionMode.NONE)
            task_list.add_css_class("boxed-list")
            task_list.connect("row-activated", self._on_task_activated)
            page.append(task_list)

            self.view_stack.add_titled(page, view_id, view_id.capitalize())
            setattr(self, f"list_{view_id}", task_list)

        self.sidebar.select_row(self.sidebar.get_row_at_index(0))

    def _on_sidebar_activated(self, listbox, row: Adw.ActionRow):
        # view_id = row.get_title().split(" ")[1].lower()
        # if "сегодня" in view_id:
        #     view_id = "today"
        view_id = row.view_id
        logger.info(f"Sidebar activated: {view_id}")
        self._load_view(view_id)

    def _load_view(self, view_id: str):
        self.view_stack.set_visible_child_name(view_id)

        # Populate widget asyncronously if available
        child = self.view_stack.get_child_by_name(view_id)
        if hasattr(child, "populate"):
            child.populate()

        # Выделяем навигацию
        # for row in self.sidebar:
        #     row.set_selected(False)

        # Асинхронная загрузка
        # current_list = getattr(self, f"list_{view_id}")
        # current_list.remove_all()
        # self.task_widgets.clear()

        # self.loader.load_async(
        #     quadrant=filters[view_id]["quadrant"],
        #     status=filters[view_id]["status"],
        #     callback=lambda tasks: self._render_tasks(tasks, current_list, view_id),
        # )

    def _render_tasks(self, tasks: list, listbox: Gtk.ListBox, view_id: str):
        for t in tasks:
            row = Adw.ActionRow(
                title=t.title,
                subtitle=f"{t.priority.upper()} | {t.due_date or 'без срока'}",
            )
            row.set_activatable(True)
            row.task_id = t.id
            row.task_quadrant = t.quadrant

            # Иконки/статус
            if t.status == "done":
                row.set_opacity(0.5)
            if t.priority == "high":
                row.add_prefix(Gtk.Image.new_from_icon_name("dialog-warning-symbolic"))

            listbox.append(row)
            self.task_widgets[t.id] = row
        return False

    def _on_task_activated(self, listbox, row):
        # Toggle completion по клику
        self.loader.complete_async(
            row.task_id, lambda ok: self._toast("✅ Выполнено") if ok else None
        )
        row.get_parent().remove(row)
        del self.task_widgets[row.task_id]

    def _setup_shortcuts(self):
        ctrl = Gtk.ShortcutController()
        self.add_controller(ctrl)

        # 1-4 → перемещение между квадрантами
        for q in range(1, 5):
            key = f"{q}"
            action = Gtk.CallbackAction.new(lambda widget, q=q: self._move_selected(q))
            ctrl.add_shortcut(
                Gtk.Shortcut.new(Gtk.ShortcutTrigger.parse_string(key), action)
            )

        # Space → отметить выполненным
        space_act = Gtk.CallbackAction.new(lambda w, f: self._complete_selected())
        ctrl.add_shortcut(
            Gtk.Shortcut.new(Gtk.ShortcutTrigger.parse_string("space"), space_act)
        )

    def _move_selected(self, quadrant: int):
        # В MVP: перемещаем последнюю активную или первую в списке
        # В production: привязать к Gtk.SelectionModel
        self._toast(f"📦 Перемещено в квадрант {quadrant}")

    def _complete_selected(self):
        self._toast("⌨️ Space: отметка задачи (выдели строку в ListModel)")

    def _toast(self, msg: str):
        self.toast_overlay.add_toast(Adw.Toast(title=msg, timeout=2))

    def show_quick_capture(self):
        quick_capture = QuickAddDialog()
        quick_capture.present(self)

    def show_project_add(self):
        logger.debug("Show project add dialog")
        self.show_toast("📝 Добавить проект")
        self.show_create_dialog()

    def show_project_edit(self):
        logger.debug("Show project edit dialog")
        self.show_toast("✏️ Редактировать проект")

    def show_project_delete(self):
        logger.debug("Show project delete dialog")
        self.show_toast("🗑️ Удалить проект")

    def show_create_dialog(self):
        # Будем вызывать из главного окна или через action
        dialog: Adw.AlertDialog = Adw.AlertDialog(
            heading="Новый проект",
            body="Введите название проекта",
        )
        # dialog.add_responses("cancel", "Отмена", "create", "Создать")
        dialog.add_response("create", "Создать")
        dialog.add_response("cancel", "Отмена")
        dialog.set_response_appearance("create", Adw.ResponseAppearance.SUGGESTED)

        entry = Gtk.Entry(placeholder_text="Название проекта...")
        dialog.set_extra_child(entry)

        def on_response(dlg, resp):
            if resp == "create":
                if name := entry.get_text().strip():
                    project_service.create_project(name=name)
            dlg.close()

        dialog.connect("response", on_response)
        dialog.present(self)
