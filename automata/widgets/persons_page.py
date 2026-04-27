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

from automata.models import Person
from automata.services import person_service


class PersonItem(GObject.GObject):
    __gtype_name__ = "PersonItem"

    def __init__(self, person: Person) -> None:
        super().__init__()
        self.person = person

    @GObject.Property
    def name(self) -> str | None:
        if not self.person:
            return None
        return str(self.person.name)

    @GObject.Property
    def email(self) -> str | None:
        if not self.person:
            return None
        return str(self.person.email)

    @GObject.Property
    def team(self) -> str | None:
        if not self.person or not self.person.team:
            return None
        return str(self.person.team)

    @property
    def role(self) -> str | None:
        if not self.person or not self.person.role:
            return None
        return str(self.person.role)


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/persons-page.ui")
class PersonsPage(Adw.NavigationPage):
    __gtype_name__ = "PersonsPage"

    person_list_view: Gtk.ListView = Gtk.Template.Child()
    selection: Gtk.MultiSelection = Gtk.Template.Child()
    loading_bar: Gtk.ProgressBar = Gtk.Template.Child()

    _thread: threading.Thread | None = None
    loading = GObject.Property(type=bool, default=False)

    def __init__(self):
        super().__init__()
        self.list_store = Gio.ListStore(item_type=PersonItem)

    def populate(self):
        self._thread = threading.Thread(target=self._load_persons)
        self.loading = True
        self._thread.start()

    def _load_persons(self):
        persons = person_service.get_all_persons()
        self.loading = False

        GLib.idle_add(self.list_store.remove_all)
        for person in persons:
            GLib.idle_add(self.list_store.append, PersonItem(person))
