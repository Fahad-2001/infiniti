from odoo import fields, models


class TaskType(models.Model):
    _name = 'task.type'

    name = fields.Char(required=True)