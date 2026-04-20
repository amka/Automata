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


import sys
from gettext import gettext as _
from pathlib import Path

from gi.repository import Adw, Gdk, Gio, GLib, Gtk
from loguru import logger

# from automata.db.client import DatabaseClient
from automata.core.database import close_db, init_db
from automata.window import AutomataWindow


class AutomataApplication(Adw.Application):
    """The main application singleton class."""

    __gtype_name__ = "AutomataApplication"

    def __init__(self):
        super().__init__(
            application_id="com.tenderowl.automata",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
            resource_base_path="/com/tenderowl/automata",
        )

        self.connect("shutdown", self.on_shutdown)

        self.create_action("quit", lambda *_: self.quit(), ["<control>q"])
        self.create_action("about", self.on_about_action)
        self.create_action("preferences", self.on_preferences_action)
        self.create_action(
            "quick-capture", self.on_quick_capture_action, ["<control>n"]
        )
        self.create_action("project.create", self._on_project_create_action)
        self.create_action("project.edit", self._on_project_edit_action)
        self.create_action("project.delete", self._on_project_delete_action)

        action = Gio.SimpleAction.new("show-toast", GLib.VariantType("s"))
        action.connect("activate", self.on_toast_action)
        self.add_action(action)

    @property
    def active_window(self) -> AutomataWindow | None:
        return self.get_active_window()

    def do_startup(self) -> None:
        Adw.Application.do_startup(self)
        logger.info("🚀 Application startup")

        self.load_resources()

        init_db()

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = AutomataWindow(application=self)
        win.present()

    def on_shutdown(self, _app) -> None:
        close_db()
        logger.info("🛑 Application shutdown")

    def load_resources(self):
        provider = Gtk.CssProvider()
        provider.load_from_resource("/com/tenderowl/automata/automata.css")
        if display := Gdk.Display.get_default():
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(
            application_name="Automata",
            application_icon="com.tenderowl.automata",
            developer_name="Andrey Maksimov",
            version="0.1.0",
            # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
            translator_credits=_("translator-credits"),
            developers=["Andrey Maksimov"],
            copyright="© 2026 Andrey Maksimov",
        )
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print("app.preferences action activated")

    def on_quick_capture_action(self, widget, _):
        """Callback for the app.quick-capture action."""
        if self.active_window:
            self.active_window.show_quick_capture()

    def _on_project_create_action(self, widget, _):
        """Callback for the project.add action."""
        if self.active_window:
            self.active_window.show_project_add()

    def _on_project_edit_action(self, widget, _):
        """Callback for the project.edit action."""
        if self.active_window:
            self.active_window.show_project_edit()

    def _on_project_delete_action(self, widget, _):
        """Callback for the project.delete action."""
        if self.active_window:
            self.active_window.show_project_delete()

    def on_toast_action(self, _action, param):
        """Callback for the toast action."""
        if self.active_window:
            self.active_window.show_toast(param.get_string())

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""

    app = AutomataApplication()
    return app.run(sys.argv)
