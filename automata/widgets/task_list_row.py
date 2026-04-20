from curses import setupterm

from gi.repository import Adw, Gio, GLib, GObject, Gtk

from automata.core.models import Task


class TaskItem(GObject.GObject):
    __gtype_name__ = "TaskItem"

    def __init__(self, task: Task) -> None:
        super().__init__()
        self.task = task

    @GObject.Property
    def title(self) -> str | None:
        if not self.task:
            return None
        return str(self.task.title)

    @GObject.Property
    def description(self) -> str | None:
        if not self.task:
            return None
        return str(self.task.description)

    @GObject.Property
    def due_date(self) -> str | None:
        if not self.task or not self.task.due_date:
            return None
        return date(
            self.task.due_date.year, self.task.due_date.month, self.task.due_date.day
        ).strftime("%x")

    @property
    def status(self) -> bool:
        if not self.task:
            return False
        return self.task.status


@Gtk.Template(resource_path="/com/tenderowl/automata/ui/task_list_row.ui")
class TaskListRow(Gtk.Box):
    __gtype_name__ = "TaskListRow"

    title: Gtk.Label = Gtk.Template.Child()
    description: Gtk.Label = Gtk.Template.Child()
    due_date: Gtk.Label = Gtk.Template.Child()
    status_checkbox: Gtk.CheckButton = Gtk.Template.Child()

    _task: Task | None

    def __init__(self, task: Task | None = None) -> None:
        super().__init__()
        self._task = task

    @GObject.Property(type=GObject.TYPE_PYOBJECT)
    def task(self) -> Task | None:
        return self._task

    @task.setter
    def task(self, value: TaskItem) -> None:
        self._task = value
        self.title.set_label(str(value.title))
        if value.description:
            self.description.set_label(value.description)
        self.description.set_visible(bool(value.description))
        if value.due_date:
            self.due_date.set_label(value.due_date)
        self.status_checkbox.set_active(value.status)
