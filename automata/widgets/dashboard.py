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

from gi.repository import Adw, Gio, GLib, Gtk

from automata.services import TaskService


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/dashboard.ui")
class DashboardPage(Gtk.Box):
    __gtype_name__ = "Dashboard"

    task_list_view: Gtk.ListView = Gtk.Template.Child()
    selection: Gtk.SingleSelection = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self.task_model = Gio.ListStore()
        self.selection.set_model(self.task_model)

    def load_today_tasks(self):
        # asyncio.create_task(self._load_tasks())
        pass

    async def _load_tasks(self):
        tasks = await TaskService.get_today_tasks()

        # Обновляем UI только в главном потоке
        GLib.idle_add(self._update_task_list, tasks)

    def _update_task_list(self, tasks):
        # очищаем список и добавляем задачи
        self.task_model.remove_all()
        for task in tasks:
            self.task_model.append(task.title)
        return False  # обязательно для idle_add
