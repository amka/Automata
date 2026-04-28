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

import os
from gettext import gettext as _

from gi.repository import Adw, Gio, GObject, Gtk
from loguru import logger

from automata.services import note_service, task_service


@Gtk.Template(
    resource_path="/com/tenderowl/automata/ui/setup-wizard/page-import-context.ui"
)
class SetupWizardImportContextPage(Adw.Bin):
    __gtype_name__ = "SetupWizardImportContextPage"

    def __init__(self):
        super().__init__()

    @Gtk.Template.Callback()
    def _on_folder_select_clicked(self, _sender: Gtk.Widget):
        self.select_folder()

    def select_folder(self, filetype: str = "csv"):
        """
        Open a file dialog to select a CSV or vCard file for import.

        args:
            filetype (str): The type of file to select, either "csv" or "vcard".
        """

        def _on_folder_selected(dialog, result):
            try:
                folder = dialog.select_folder_finish(result)
                if folder:
                    logger.debug(f"Selected file: {folder.get_path()}")
                    self.import_markdown(folder.get_path())
            except Exception as e:
                logger.error(f"Error opening file: {e}")

        # Init the file dialog
        dialog = Gtk.FileDialog(accept_label=_("Import notes"))
        dialog.select_folder(None, None, _on_folder_selected)

    def import_markdown(self, file_path):
        for root, _dirnames, files in os.walk(file_path):
            for file in files:
                if file.endswith(".md"):
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()

                        # Parsing rules:
                        # - Headign → create WorkItem of Note or Project type (or tag #project)
                        # - `- [ ]` Task → WorkItem типа task, status inbox
                        # - `@Name` → link to person (search by name)
                        # - `#tag` → tags + item_tags
                        # @TODO: create smart parser
                        title = None
                        for line in content.split("\n"):
                            if line.startswith("# "):
                                title = line[2:].strip()
                                # Создаём проект или заметку
                                #
                                note_service.add_note(
                                    title=title, body=content, owner=1
                                )
                            elif line.startswith("- [ ]"):
                                task_title = line[5:].strip()
                                # Парсим @mentions и #tags
                                task_service.create_task(title=task_title, owner=1)
