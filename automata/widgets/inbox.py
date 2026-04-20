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
from datetime import date

from gi.repository import Adw, Gio, GLib, GObject, Gtk

from automata.core.models import Task
from automata.services import TaskService
from automata.widgets.task_list_row import TaskItem, TaskListRow


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/inbox.ui")
class InboxPage(Gtk.Box):
    __gtype_name__ = "Inbox"

    task_list_view: Gtk.ListView = Gtk.Template.Child()
    selection: Gtk.MultiSelection = Gtk.Template.Child()
    loading_bar: Gtk.ProgressBar = Gtk.Template.Child()

    _thread: threading.Thread | None = None
    loading = GObject.Property(type=bool, default=False)

    def __init__(self):
        super().__init__()

        self.list_store = Gio.ListStore(item_type=TaskItem)
        self.selection.set_model(self.list_store)

        self.loading_bar.bind_property(
            "visible", self, "loading", GObject.BindingFlags.SYNC_CREATE
        )

    def populate(self):
        self._thread = threading.Thread(target=self._load_tasks)
        self.loading = True
        self._thread.start()

    def _load_tasks(self):
        tasks = TaskService.get_inbox_tasks()
        self.loading = False

        GLib.idle_add(self.list_store.remove_all)
        for task in tasks:
            GLib.idle_add(self.list_store.append, TaskItem(task))

    @Gtk.Template.Callback()
    def _on_factory_bind(
        self,
        factory: Gtk.SignalListItemFactory,
        list_item: Gtk.ListItem,
    ) -> None:
        item = list_item.get_item()
        row: TaskListRow = list_item.get_child()
        row.task = item

    @Gtk.Template.Callback()
    def _on_factory_setup(
        self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem
    ) -> None:
        list_item.set_child(TaskListRow())
