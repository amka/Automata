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

from gi.repository import Adw, GObject, Gtk
from loguru import logger


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/sidebar.ui")
class Sidebar(Adw.NavigationPage):
    __gtype_name__ = "Sidebar"

    __gsignals__ = {
        "section-selected": (GObject.SignalFlags.RUN_LAST, None, (str,)),
    }

    sections_list_box: Gtk.ListBox = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

    @Gtk.Template.Callback()
    def _on_section_selected(self, list_box: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        section_name = row.get_name()
        logger.debug(f"Section selected: {section_name}")
        self._emit_section_selected(section_name)

    def _emit_section_selected(self, tag: str) -> None:
        self.emit("section-selected", tag)
