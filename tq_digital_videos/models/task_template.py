from odoo import models, fields


class TaskTemplates(models.Model):
    _name = 'task.template'
    _rec_name = 'name'

    name = fields.Char(required=True)
    subtask_ids = fields.One2many('task.template.line', 'task_temp_id')


class TaskTemplatesLine(models.Model):
    _name = 'task.template.line'

    # task_id = fields.Many2one('project.task', required=True)
    task_temp_id = fields.Many2one('task.template')
    name = fields.Char(required=True)