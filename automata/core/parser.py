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

import re
from datetime import datetime, timedelta


def parse_quick(text: str) -> dict:
    raw = text.strip()
    task = {
        "title": raw,
        "quadrant": 0,
        "priority": "medium",
        "tags": [],
        "due_date": None,
        "assignee": None,
    }

    # Приоритеты
    if re.search(r"!high|!urgent|!critical", raw, re.I):
        task["priority"] = "high"
        task["title"] = re.sub(
            r"!high|!urgent|!critical", "", task["title"], flags=re.I
        ).strip()
    elif re.search(r"!low", raw, re.I):
        task["priority"] = "low"
        task["title"] = re.sub(r"!low", "", task["title"], flags=re.I).strip()

    # Даты
    due = re.search(r"(today|tomorrow|in\s+(\d+)\s*(day|d))", raw, re.I)
    if due:
        now = datetime.now().date()
        if "today" in due.group():
            task["due_date"] = str(now)
        elif "tomorrow" in due.group():
            task["due_date"] = str(now + timedelta(days=1))
        else:
            task["due_date"] = str(now + timedelta(days=int(due.group(2))))
        task["title"] = re.sub(
            r"(today|tomorrow|in\s+\d+\s*(day|d))", "", task["title"], flags=re.I
        ).strip()

    # Теги и делегирование
    task["tags"] = re.findall(r"#(\w+)", raw)
    ass = re.search(r"@(\w+)", raw)
    if ass:
        task["assignee"] = ass.group(1)
        task["quadrant"] = 3  # Delegate
        task["title"] = re.sub(r"#\w+|@\w+", "", task["title"]).strip()
    else:
        task["title"] = re.sub(r"#\w+", "", task["title"]).strip()

    return task
