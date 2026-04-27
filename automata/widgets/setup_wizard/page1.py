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

from gettext import gettext as _

from gi.repository import Adw, Gio, GObject, Gtk
from loguru import logger

from automata.services.person_service import person_service
from automata.widgets.persons_page import PersonItem


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/setup-wizard/page-1.ui")
class SetupWizardPage1(Adw.Bin):
    __gtype_name__ = "SetupWizardPage1"

    name_entry: Adw.EntryRow = Gtk.Template.Child()
    role_entry: Adw.EntryRow = Gtk.Template.Child()
    email_entry: Adw.EntryRow = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

    def submit(self):
        self.name_entry.remove_css_class("error")
        self.name_entry
        self.email_entry.remove_css_class("error")

        user_name = self.name_entry.get_text().strip()
        user_role = self.role_entry.get_text().strip()
        user_email = self.email_entry.get_text().strip()

        if not user_name:
            # self.name_entry.add_suffix(Gtk.Image(icon_name="dialog-warning-symbolic"))
            self.name_entry.add_css_class("error")
            return

        if not self._validate_email(user_email):
            # self.email_entry.add_suffix(Gtk.Image(icon_name="dialog-warning-symbolic"))
            self.email_entry.add_css_class("error")
            return

        person_service.add_person(
            name=user_name, role=user_role, email=user_email, is_me=True
        )

    def _validate_email(self, email: str) -> bool:
        import re

        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(pattern, email) is not None
