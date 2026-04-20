# # MIT License
# #
# # Copyright (c) 2026 Andrey Maksimov
# #
# # Permission is hereby granted, free of charge, to any person obtaining a copy
# # of this software and associated documentation files (the "Software"), to deal
# # in the Software without restriction, including without limitation the rights
# # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # copies of the Software, and to permit persons to whom the Software is
# # furnished to do so, subject to the following conditions:
# #
# # The above copyright notice and this permission notice shall be included in all
# # copies or substantial portions of the Software.
# #
# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# # SOFTWARE.
# #
# # SPDX-License-Identifier: MIT

# from datetime import date, datetime

# from tortoise import fields, models


# class Task(models.Model):
#     id = fields.IntField(pk=True)
#     title = fields.CharField(max_length=500)
#     description = fields.TextField(null=True)
#     status = fields.CharField(max_length=20, default="todo")
#     priority = fields.IntField(default=3)
#     eisenhower = fields.CharField(
#         max_length=20, null=True
#     )  # do, schedule, delegate, delete
#     due_date = fields.DateField(null=True)
#     start_date = fields.DateField(null=True)
#     completed_at = fields.DatetimeField(null=True)
#     time_estimate = fields.IntField(null=True)  # minutes
#     time_spent = fields.IntField(default=0)

#     project: fields.ForeignKeyRelation["Project"] = fields.ForeignKeyField(
#         "models.Project", related_name="tasks", null=True, on_delete=fields.SET_NULL
#     )
#     parent_task: fields.ForeignKeyRelation["Task"] = fields.ForeignKeyField(
#         "models.Task", related_name="subtasks", null=True, on_delete=fields.CASCADE
#     )

#     jira_key = fields.CharField(max_length=50, null=True)
#     incident_id = fields.CharField(max_length=100, null=True)
#     # список строк, удобно для тегов
#     tags: fields.JSONField = fields.JSONField(default=list)

#     created_at = fields.DatetimeField(auto_now_add=True)
#     updated_at = fields.DatetimeField(auto_now=True)

#     class Meta:
#         table = "tasks"
