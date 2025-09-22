import datetime
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class LeadGeneration(models.Model):
    _name = 'lead.generation'
    _rec_name = 'page_seq'
    _description = 'Lead Generation'
    _inherit = ["mail.thread"]

    page_seq = fields.Char(string="Page ID", readonly=True, default='New')
    platform_id = fields.Many2one('project.platform', string="Social Media Network", tracking=True)
    page_name = fields.Char(required=True, tracking=True)
    page_link = fields.Char(required=True, tracking=True)
    lead_generation_lines = fields.One2many('lead.generation.line', 'lead_id')
    followers = fields.Char(tracking=True)
    lines_count = fields.Integer(compute='count_lead_generation_lines', string="Number of Contacts")
    create_date_copy = fields.Datetime(compute="get_create_date_and_user", store=True)
    create_uid_copy = fields.Many2one('res.users', compute="get_create_date_and_user", store=True)

    @api.depends('create_date', 'create_uid')
    def get_create_date_and_user(self):
        for rec in self:
            rec.create_date_copy = False
            rec.create_uid_copy = False
            if rec.create_date:
                rec.create_date_copy = rec.create_date
            if rec.create_uid:
                rec.create_uid_copy = rec.create_uid

    @api.depends('lead_generation_lines')
    def count_lead_generation_lines(self):
        for rec in self:
            rec.lines_count = len(rec.lead_generation_lines)

    def export_data(self, fields_to_export):
        if self.env.user.has_group("tq_lead_generation.lead_not_export_group"):
            raise ValidationError("You are not allowed to Export this record.")
        return super(LeadGeneration, self).export_data(fields_to_export)

    def unlink(self):
        for rec in self:
            rec.lead_generation_lines.unlink()
        res = super(LeadGeneration, self).unlink()
        return res

    @api.model
    def create(self, vals):
        if vals.get('page_seq', 'New') == 'New':
            vals['page_seq'] = self.env['ir.sequence'].next_by_code(
                'lead.generation.seq') or '/'
        return super(LeadGeneration, self).create(vals)

    # @api.constrains('platform_id', 'page_link')
    # def duplicate_check_constrains(self):
    #     for rec in self:
    #         full_name = rec.platform_id.name + rec.page_link
    #         all_records = self.search([('id', 'not in', [rec.id])])
    #         if any(all_records.filtered(lambda x: (x.platform_id.name + x.page_link) == full_name)):
    #             raise ValidationError("This Media type with this Page link is already exist!")


class LeadGenerationLine(models.Model):
    _name = 'lead.generation.line'

    email = fields.Char(string="Email", required=True)
    user_id = fields.Many2one('res.users', string="Contact User", readonly=True, default=lambda self: self.env.user)
    lead_id = fields.Many2one('lead.generation')
    is_exported = fields.Boolean(string="Exported", readonly=True)
    export_datetime = fields.Datetime(string="Export Datetime", readonly=True)
    website = fields.Char()
    phone = fields.Char()
    name = fields.Char()
    platform_id = fields.Many2one('project.platform', related='lead_id.platform_id', string="Social Media Network", store=True)

    def export_data(self, fields_to_export):
        res = super(LeadGenerationLine, self).export_data(fields_to_export)
        for rec in self.sudo().browse(self.ids):
            rec.is_exported = True
            rec.export_datetime = datetime.datetime.now()
        return res

    @api.onchange('email')
    def onchange_validate_email(self):
        if self.email:
            if self.validate_email(self.email):
                raise ValidationError(_("Invalid Email Format"))

    def validate_email(self, email):
        if not (re.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)):
            return True
        return False