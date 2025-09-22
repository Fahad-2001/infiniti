from odoo import models, fields, api


class CalendarEventInherit(models.Model):
    _inherit = 'calendar.event'

    project_id = fields.Many2one('project.project')
    task_id = fields.Many2one('project.task')
    status_id = fields.Many2one('calendar.status')
    color = fields.Char(related='status_id.color')

    def intersection(self, task_ids, cal_tasks):
        final = [value for value in task_ids if value not in cal_tasks]
        return final

    @api.onchange('project_id')
    def filter_tasks(self):
        for rec in self:
            filter_tasks = []
            if rec.project_id:
                task_ids = self.env['project.task'].search([('project_id', '=', rec.project_id.id)]).filtered(lambda x: x.stage_id.is_closed).ids
                cal_tasks = self.env['calendar.event'].search([]).filtered(lambda x: x.id != rec.id).mapped('task_id').ids
                filter_tasks = rec.intersection(task_ids, cal_tasks)
                domain = {'task_id': [('id', 'in', filter_tasks)]}
                return {'domain': domain}
            else:
                domain = {'task_id': [('id', 'in', filter_tasks)]}
                return {'domain': domain}

    @api.model
    def create(self, vals_list):
        rec = super(CalendarEventInherit, self).create(vals_list)
        rec.task_id.calendar_id = rec.id
        rec.task_id.calendar_date = rec.start
        rec.task_id.calendar_status_id = rec.status_id.id
        return rec

    def write(self, vals):
        if vals.get('task_id', None):
            if self.task_id.calendar_id.id == self.id:
                self.task_id.calendar_id = False
                self.task_id.calendar_date = False
                self.task_id.calendar_status_id = False
        res = super(CalendarEventInherit, self).write(vals)
        for rec in self:
            rec.task_id.calendar_id = rec.id
            rec.task_id.calendar_date = rec.start
            rec.task_id.calendar_status_id = rec.status_id.id
        return res


class CalendarStatus(models.Model):
    _name = "calendar.status"

    name = fields.Char(required=True)
    color = fields.Char()
