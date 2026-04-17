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

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
import threading

from gi.repository import Adw, Gio, GLib, Gtk

from automata.core.parser import parse_quick
from automata.db.client import DatabaseClient


class QuickCapture(Adw.Window):
    def __init__(self):
        super().__init__()
        self.set_title("⚡ Quick Capture")
        self.set_default_size(520, 110)

        self.db = DatabaseClient()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self.entry = Adw.EntryRow(title="Задача: #теги !приоритет @исполнитель дата")
        self.entry.set_activates_default(True)
        box.append(self.entry)

        btn = Gtk.Button(label="Сохранить")
        btn.connect("clicked", lambda _: self.submit())
        box.append(btn)

        self.set_content(box)
        self.connect("close-request", lambda w: w.hide() or True)

    def submit(self):
        text = self.entry.get_text().strip()
        if not text:
            return

        task = parse_quick(text)
        # БД в отдельном потоке, UI обновляем через GLib
        threading.Thread(target=self._save_bg, args=(task,), daemon=True).start()
        self.entry.set_text("")
        self.hide()

    def _save_bg(self, task):
        self.db.execute(
            "INSERT INTO tasks (title, priority, quadrant, tags, assignee, due_date) VALUES (?,?,?,?,?,?)",
            (
                task["title"],
                task["priority"],
                task["quadrant"],
                ",".join(task["tags"]),
                task["assignee"],
                task["due_date"],
            ),
        )
        self.db.commit()
        # Уведомление
        GLib.idle_add(self._show_notification, task["title"])

    def _show_notification(self, title):
        notif = Gio.Notification.new("✅ Захвачено")
        notif.set_body(f"{title} → Inbox/Delegate")
        Gio.Application.get_default().send_notification("task_saved", notif)
        return False
