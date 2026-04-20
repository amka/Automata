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

from gi.repository import Adw, GLib, Gtk

# from automata.core.db_worker import db_worker
# from automata.models import Task
from automata.core.models import Task
from automata.services.task_service import TaskService


class QuickAddDialog(Adw.Dialog):
    def __init__(self):
        super().__init__(
            title="Быстрое добавление задачи",
            # body="Введите название задачи. Можно добавить детали ниже.",
        )

        # self.set_close_response("cancel")
        # self.add_responses(
        #     ("cancel", "Отмена"),
        #     ("add", "Добавить в Inbox"),
        #     ("add_process", "Добавить и обработать"),
        # )
        # self.set_response_appearance("add", Adw.ResponseAppearance.SUGGESTED)

        # Основное поле
        self.title_entry = Adw.EntryRow(title="Название задачи")
        self.title_entry.set_activates_default(True)

        # Группа дополнительных полей
        self.details_group = Adw.PreferencesGroup(title="Детали")

        self.desc_row = Adw.EntryRow(title="Описание")
        self.due_row = Adw.ActionRow(title="Срок")  # позже заменишь на Date selector
        self.priority_row = Adw.ComboRow(title="Приоритет")

        self.details_group.add(self.desc_row)
        self.details_group.add(self.due_row)
        self.details_group.add(self.priority_row)

        # Добавляем в content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.append(self.title_entry)
        box.append(self.details_group)
        box.set_margin_bottom(12)
        box.set_margin_top(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        cancel_button = Gtk.Button(label="Отмена")
        save_button = Gtk.Button(label="Сохранить")
        cancel_button.connect("clicked", self._on_close_response)
        save_button.connect("clicked", self._on_save_response)

        bottom_bar = Gtk.Box(spacing=12)
        bottom_bar.set_margin_bottom(12)
        bottom_bar.set_margin_top(12)
        bottom_bar.set_margin_start(12)
        bottom_bar.set_margin_end(12)
        bottom_bar.append(cancel_button)
        bottom_bar.append(save_button)

        content = Adw.ToolbarView(content=box)
        content.add_top_bar(Adw.HeaderBar())
        content.add_bottom_bar(bottom_bar)
        self.set_child(content)

    def _on_save_response(self, *args):
        self._save_task(False)

    def _on_close_response(self, *args):
        self.close()

    def _save_task(self, open_editor: bool):
        title = self.title_entry.get_text().strip()
        if not title:
            return

        try:
            task = TaskService.quick_create(
                title=title, status="todo", priority=3, tags=[]
            )

            GLib.idle_add(self._post_save, task)
        except Exception as e:
            print(f"Error: {e}")

    def _post_save(self, task: Task):
        # Обновить списки в Dashboard/Inbox
        # Если open_editor — открыть детальную карточку задачи
        self.close()
        return False
