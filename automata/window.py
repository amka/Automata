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

from termios import VINTR
from typing import Dict

from gi.repository import Adw, Gio, Gtk
from loguru import logger

from automata.core.task_loader import TaskLoader
from automata.db.client import DatabaseClient
from automata.db.repo import TaskDAO
from automata.models.task import Task
from automata.widgets.quick_capture import QuickCapture


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/window.ui")
class AutomataWindow(Adw.ApplicationWindow):
    __gtype_name__ = "AutomataWindow"

    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()
    split_view: Adw.NavigationSplitView = Gtk.Template.Child()
    sidebar_page: Adw.NavigationPage = Gtk.Template.Child()
    sidebar: Gtk.ListBox = Gtk.Template.Child()
    content_page: Adw.NavigationPage = Gtk.Template.Child()
    view_stack: Gtk.Stack = Gtk.Template.Child()

    settings: Gio.Settings

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Инициализация слоёв
        self.db = DatabaseClient()
        self.dao = TaskDAO(self.db)
        self.loader = TaskLoader(self.dao)
        self.quick_capture = QuickCapture()

        # Хранилище UI-состояния
        self.task_widgets: Dict[int, Gtk.ListBoxRow] = {}

        self._build_ui()
        self._setup_shortcuts()
        self._load_view("today")

        self._bind_settings()

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

    def show_toast(self, message: str):
        toast = Adw.Toast.new(message)
        self.toast_overlay.add_toast(toast)

    def _build_ui(self):
        self.sidebar.connect("row-activated", self._on_sidebar_activated)

        views = [
            ("today", "📅 Сегодня", "Сфокусированный список на день"),
            ("inbox", "📥 Inbox", "Сырой поток задач"),
            ("matrix", "📊 Матрица", "4 квадранта приоритетов"),
            ("delegated", "⏳ Ожидание", "Делегировано и на контроле"),
            ("projects", "🗺️ Проекты", "Радар инициатив"),
        ]
        for view_id, title, desc in views:
            row = Adw.ActionRow(title=title, subtitle=desc)
            row.set_activatable(True)
            row.view_id = view_id
            self.sidebar.append(row)
            setattr(self, f"nav_{view_id}", row)

        # CONTENT

        # Создаём страницы-списки
        for view_id in ["today", "inbox", "matrix", "delegated", "projects"]:
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

    def _on_sidebar_activated(self, listbox, row: Adw.ActionRow):
        # view_id = row.get_title().split(" ")[1].lower()
        # if "сегодня" in view_id:
        #     view_id = "today"
        view_id = row.view_id
        logger.info(f"Sidebar activated: {view_id}")
        self._load_view(view_id)

    def _load_view(self, view_id: str):
        # Маппинг навигации на фильтры БД
        filters = {
            "today": {
                "quadrant": None,
                "status": "active",
            },  # Загружается в QuickCapture logic
            "inbox": {"quadrant": 0, "status": "active"},
            "matrix": {
                "quadrant": None,
                "status": "active",
            },  # Пока flat-list, позже grid
            "delegated": {"quadrant": 3, "status": "active"},
            "projects": {"quadrant": None, "status": "active"},
        }

        # Обновляем заголовок
        titles = {
            "today": "Сегодня",
            "inbox": "Inbox",
            "matrix": "Матрица Эйзенхауэра",
            "delegated": "Ожидание",
            "projects": "Проекты",
        }
        self.content_page.set_title(titles.get(view_id, view_id))
        self.view_stack.set_visible_child_name(view_id)

        # Выделяем навигацию
        # for row in self.sidebar:
        #     row.set_selected(False)

        # Асинхронная загрузка
        current_list = getattr(self, f"list_{view_id}")
        current_list.remove_all()
        self.task_widgets.clear()

        self.loader.load_async(
            quadrant=filters[view_id]["quadrant"],
            status=filters[view_id]["status"],
            callback=lambda tasks: self._render_tasks(tasks, current_list, view_id),
        )

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
        self.quick_capture.show()
        self.quick_capture.present()
