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

from automata.widgets.setup_wizard import (
    SetupWizardAddOwnerPage,
    SetupWizardFinishPage,
    SetupWizardImportContactsPage,
    SetupWizardImportContextPage,
    SetupWizardSetGoalsPage,
)


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/setup-wizard/setup-wizard.ui")
class SetupWizard(Adw.Dialog):
    __gtype_name__ = "SetupWizard"

    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()
    pages: Gtk.Stack = Gtk.Template.Child()
    page1: SetupWizardAddOwnerPage = Gtk.Template.Child()
    page2: SetupWizardImportContactsPage = Gtk.Template.Child()
    page3: SetupWizardImportContextPage = Gtk.Template.Child()
    page4: SetupWizardSetGoalsPage = Gtk.Template.Child()
    page5: SetupWizardFinishPage = Gtk.Template.Child()

    def __init__(self, settings: Gio.Settings):
        super().__init__()
        self.settings = settings

        step = self.settings.get_int("onboarding-step")
        if step > 1 and step < 5:

            def _on_dialog_response(dialog: Adw.AlertDialog, response: str):
                if response == "restart":
                    self.settings.set_int("onboarding-step", 1)
                # else:
                #     self.settings.set_int(
                #         "onboarding-step", self.settings.get_int("onboarding-step") + 1
                #     )
                self._set_page(self.settings.get_int("onboarding-step"))

            # Предложить продолжить
            dialog = Adw.AlertDialog(
                heading="Продолжить настройку?",
                body=f"Вы остановились на шаге {step + 1} из 5",
            )
            dialog.add_response("restart", "Начать заново")
            dialog.add_response("continue", "Продолжить")
            dialog.set_response_appearance("continue", Adw.ResponseAppearance.SUGGESTED)

            dialog.connect("response", _on_dialog_response)
            dialog.present(self)
        # self._set_page(step)

    def _set_page(self, step_number: int):
        self.pages.set_visible_child_name(f"page-{step_number}")
        page = self.pages.get_visible_child()

        print(page)

        if hasattr(page, "populate"):
            page.populate()

    @Gtk.Template.Callback()
    def _on_back_clicked(self, _sender: Gtk.Widget):
        logger.debug("_on_back_clicked")

    @Gtk.Template.Callback()
    def _on_next_clicked(self, _sender: Gtk.Widget):
        page_name = self.pages.get_visible_child_name() or ""

        if step_number := page_name.split("-")[1]:
            step_number = int(step_number)
            match step_number:
                case 1:
                    self.handle_step_1()
                case 2:
                    self.pages.set_visible_child_name("page-3")
                case 3:
                    self.pages.set_visible_child_name("page-4")
                case 4:
                    self.pages.set_visible_child_name("page-5")
                case 5:
                    self.close()
                case _:
                    self.pages.set_visible_child_name(f"page-{step_number}")
        logger.debug("_on_next_clicked")

    @Gtk.Template.Callback()
    def _on_skip_clicked(self, _sender: Gtk.Widget):
        logger.debug("Skip clicked")
        self.settings.set_int("onboarding-step", 4)
        self.settings.set_boolean("onboarding-complete", True)
        self._set_page(self.settings.get_int("onboarding-step"))

    def handle_step_1(self):
        """
        Handle the first step of the setup wizard, validating the user's name and email.
        """

        try:
            self.page1.submit()
            self.settings.set_int("onboarding-step", 2)
        except Exception as e:
            logger.error(f"Failed to add person: {e}")
            self.toast_overlay.add_toast(Adw.Toast(title=str(e)))
            return

        self._set_page(self.settings.get_int("onboarding-step"))

    def handle_step_2(self):
        """
        Handle the second step of the setup wizard, validating the user's email.
        """
        self.settings.set_int("onboarding-step", 3)
        self._set_page(self.settings.get_int("onboarding-step"))
