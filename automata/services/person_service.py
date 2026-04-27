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
from gi.repository.Adw import PreferencesDialog

from automata.models import Person


class PersonSignal(enum.Enum):
    PERSON_ADDED = "person-added"
    PERSON_REMOVED = "person-removed"
    PERSON_UPDATED = "person-updated"


class PersonService(GObject.GObject):
    __gtype_name__ = "PersonService"

    __gsignals__ = {
        PersonSignal.PERSON_ADDED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
        PersonSignal.PERSON_REMOVED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
        PersonSignal.PERSON_UPDATED.value: (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT,),
        ),
    }

    def __init__(self) -> None:
        super().__init__()

    def get_all_persons(self) -> List[Person]:
        return list(Person.select().order_by(Person.name))

    def add_person(self, **kwargs) -> Person:
        person = Person(**kwargs)
        person.save()
        self.emit(PersonSignal.PERSON_ADDED.value, person)
        return person

    def update_person(self, person_id: int, **kwargs) -> Person:
        person = Person.get_or_none(Person.id == person_id)
        if person:
            for key, value in kwargs.items():
                setattr(person, key, value)
            person.save()
            self.emit(PersonSignal.PERSON_UPDATED.value, person)
        return person

    def delete_person(self, person_id: int) -> bool:
        person = Person.get_or_none(Person.id == person_id)
        if person:
            person.delete_instance(recursive=True)  # удалит и все связанные задачи
            self.emit(PersonSignal.PERSON_REMOVED.value, person)
            return True
        return False


# Singleton instance
# Required to properly subscribe to signals
person_service = PersonService()
