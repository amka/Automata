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

from automata.models import Person
from automata.services.person_service import PersonSignal, person_service
from automata.widgets.persons_page import PersonItem


@Gtk.Template(
    resource_path="/com/tenderowl/automata/ui/setup-wizard/page-import-contacts.ui"
)
class SetupWizardImportContactsPage(Adw.Bin):
    __gtype_name__ = "SetupWizardImportContactsPage"

    # Page 2
    persons_list_view: Gtk.ListView = Gtk.Template.Child()
    filter_model: Gtk.FilterListModel = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self.persons_store = Gio.ListStore(item_type=PersonItem)
        self.filter_model.set_model(self.persons_store)

        person_service.connect(PersonSignal.PERSON_ADDED.value, self._on_person_added)

    def populate(self):
        logger.debug("Populating page 2")
        persons = person_service.get_all_persons()
        self.persons_store.remove_all()
        for person in persons:
            self.persons_store.append(PersonItem(person))

    def _on_person_added(self, _sender, person: Person):
        self.persons_store.append(PersonItem(person))

    @Gtk.Template.Callback()
    def _on_search_changed(self, _sender: Gtk.SearchEntry):
        search_term = _sender.get_text().lower()
        self.filter_model.set_filter(
            Gtk.CustomFilter.new(
                lambda item: (
                    search_term in item.person.name.lower()
                    or search_term in item.person.email.lower()
                    or search_term in item.person.role.lower()
                )
            )
        )

    @Gtk.Template.Callback()
    def _on_item_setup(self, _factory, list_item):
        row = Adw.ActionRow()
        row.set_subtitle_lines(2)
        list_item.set_child(row)

    @Gtk.Template.Callback()
    def _on_item_bind(self, _factory, list_item):
        item = list_item.get_item()
        row = list_item.get_child()
        person = item.person
        row.set_title(person.name)
        row.set_subtitle(f"{person.role}\n{person.email}")

    @Gtk.Template.Callback()
    def _on_csv_import_clicked(self, _sender: Gtk.Widget):
        logger.debug("CSV import clicked")
        self.select_file("csv")

    @Gtk.Template.Callback()
    def _on_vcard_import_clicked(self, _sender: Gtk.Widget):
        logger.debug("vCard import clicked")
        self.select_file("vcard")

    def select_file(self, filetype: str = "csv"):
        """
        Open a file dialog to select a CSV or vCard file for import.

        args:
            filetype (str): The type of file to select, either "csv" or "vcard".
        """

        def _on_file_selected(dialog, result):
            try:
                file = dialog.open_finish(result)
                if file:
                    logger.debug(f"Selected file: {file.get_path()}")
                    if filetype == "csv":
                        self.import_csv(file.get_path())
                    elif filetype == "vcard":
                        self.import_vcard(file.get_path())
            except Exception as e:
                logger.error(f"Error opening file: {e}")

        # Init the file dialog
        dialog = Gtk.FileDialog(accept_label=_("Import"))
        match filetype:
            case "csv":
                filter = Gtk.FileFilter(name="CSV files", patterns=["*.csv"])
            case "vcard":
                filter = Gtk.FileFilter(name="vCard files", patterns=["*.vcf"])
            case _:
                filter = None
        dialog.set_default_filter(filter)
        dialog.open(None, None, _on_file_selected)

    def import_csv(self, file_path):
        """
        Import a CSV file of people.

        Each row must have name, email, role, and team columns.
        """
        import csv

        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                # Check if name, email, team and role fields in reader.fieldnames
                if not all(
                    field in reader.fieldnames
                    for field in ["name", "email", "role", "team"]
                ):
                    logger.warning(
                        "CSV file must have name, email, role, and team columns"
                    )
                    return

                for row in reader:
                    try:
                        person_service.add_person(
                            name=row.get("name"),
                            email=row.get("email"),
                            role=row.get("role"),
                            team=row.get("team"),
                        )
                    except Exception as e:
                        logger.debug(f"Error importing CSV row: {str(e)}")
        except Exception as e:
            logger.error(f"Error importing CSV: {str(e)}")

    def import_vcard(self, file_path):
        logger.debug(f"Importing vCard from {file_path}")
