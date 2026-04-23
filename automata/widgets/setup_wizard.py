from gi.repository import Adw, Gtk
from loguru import logger


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/setup-wizard.ui")
class SetupWizard(Adw.Dialog):
    __gtype_name__ = "SetupWizard"

    goals_list: Adw.PreferencesGroup = Gtk.Template.Child()
    goal_entry: Gtk.Entry = Gtk.Template.Child()

    goals = []

    def __init__(self):
        super().__init__()

        self.goal_entry.grab_focus_without_selecting()

    @Gtk.Template.Callback()
    def _on_goal_add_clicked(self, _sender: Gtk.Widget):
        logger.debug("Goal add clicked")

        text = self.goal_entry.get_text()
        if not text.strip():
            return

        self.goals_list.add(Gtk.Label(label=text.strip()))
        self.goal_entry.set_text("")
