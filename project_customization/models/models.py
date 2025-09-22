# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class project_customization(models.Model):
#     _name = 'project_customization.project_customization'
#     _description = 'project_customization.project_customization'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

class Calendar(models.Model):
    _inherit = 'calendar.event'

    user_can_edit = fields.Boolean(compute='_compute_user_can_edit')
    status = fields.Selection(
        [('5', 'Draft'),
         ('6', 'Done'), ],
        'State', default='5', readonly=False)

    def action(self):
        self.write({'status':'6'})

    @api.depends('partner_ids')
    @api.depends_context('uid')
    def _compute_user_can_edit(self):
        for event in self:
            event.user_can_edit = self.env.user in event.partner_ids.user_ids + event.user_id or self.env.user.has_group('base.group_partner_manager')


class UsersInherit(models.Model):
    _inherit = 'res.users'

    project_ids = fields.Many2many('project.project', string="Projects")