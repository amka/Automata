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

import enum
from typing import List

from gi.repository import GObject

from automata.models import Note, WorkItem


class NoteSignal(enum.Enum):
    NOTE_ADDED = "note-added"
    NOTE_REMOVED = "note-removed"
    NOTE_UPDATED = "note-updated"


class NoteService(GObject.GObject):
    __gtype_name__ = "NoteService"

    __gsignals__ = {
        NoteSignal.NOTE_ADDED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
        NoteSignal.NOTE_REMOVED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
        NoteSignal.NOTE_UPDATED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
    }

    def __init__(self):
        super().__init__()

    def add_note(self, **kwargs) -> WorkItem | None:
        note = WorkItem(**kwargs)
        self.emit(NoteSignal.NOTE_ADDED.value, note)
        return note


note_service = NoteService()
