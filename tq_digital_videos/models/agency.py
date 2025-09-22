from odoo import models, fields, api, _


class Agency(models.Model):
    _name = 'res.agency'
    _inherit = ["mail.thread"]
    _rec_name = 'name'

    name = fields.Char(required=True, tracking=True)
    digital_ids = fields.One2many('digital.videos', 'agency_id')
    task_ids = fields.One2many('res.agency.task', 'agency_id', compute="compute_digital_tasks")

    def open_tasks(self):
        task_lst = []
        for line in self.digital_ids.mapped('sub_tasks_ids'):
            task_lst.append(line.task_id.id)
        return {
            'name': _('Project Tasks'),
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', task_lst)],
        }

    def open_digital_assets(self):
        return {
            'name': _('Digital Videos'),
            'view_mode': 'tree,form',
            'res_model': 'digital.videos',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.digital_ids.ids)],
        }

    @api.depends('digital_ids')
    def compute_digital_tasks(self):
        for rec in self:
            rec.task_ids = False
            for line in rec.digital_ids.mapped('sub_tasks_ids'):
                vals = {
                    'agency_id': rec.id,
                    'task_id': line.task_id.id
                }
                agency_task = rec.task_ids.create(vals)


class AgencyTaskList(models.Model):
    _name = 'res.agency.task'

    agency_id = fields.Many2one('res.agency')
    task_id = fields.Many2one('project.task')