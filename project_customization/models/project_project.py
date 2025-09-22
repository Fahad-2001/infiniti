# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritProjectProject(models.Model):
    _inherit = 'project.project'

    user_ids = fields.Many2many('res.users', string='Users')