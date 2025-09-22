from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class DigitalVideos(models.Model):
    _name = 'digital.videos'
    _inherit = ["mail.thread"]


    name = fields.Char(required=True, tracking=True)
    url_1 = fields.Char(string="URL 1", required=True, tracking=True)
    url_2 = fields.Char(string="URL 2", tracking=True)
    url_3 = fields.Char(string="URL 3", tracking=True)
    sub_tasks_ids = fields.One2many('sub.task.url', 'digital_id')
    digital_seq = fields.Char('Sequence', readonly=True, default='New')
    is_spam = fields.Boolean(string="Spam", tracking=True)
    agency_id = fields.Many2one('res.agency', string="Agency", tracking=True)
    agency_UID = fields.Char()
    tag_ids = fields.Many2many('project.tags', 'digital_asset_project_tag', string='Tags')
    media_type_id = fields.Many2one('media.type', string="Media Type")

    @api.model
    def create(self, vals):
        if vals.get('digital_seq', 'New') == 'New':
            vals['digital_seq'] = self.env['ir.sequence'].next_by_code(
                'digital.assets.seq') or '/'
        res =  super(DigitalVideos, self).create(vals)
        res.name = str(res.name).strip()
        return res

    def compute_url_validation(self, record, url):
        url_1 = self.env['digital.videos'].search([('url_1', '=', url), ('id', '!=', record._origin.id)])
        url_2 = self.env['digital.videos'].search([('url_2', '=', url), ('id', '!=', record._origin.id)])
        url_3 = self.env['digital.videos'].search([('url_3', '=', url), ('id', '!=', record._origin.id)])
        if any(url_1) or any(url_2) or any(url_3):
            all_records = url_1 or url_2 or url_3
            return all_records

    @api.onchange('url_1')
    def onchange_url_1_validation(self):
        self_url1 = str(self.url_1).strip() if self.url_1 else False
        self_url2 = str(self.url_2).strip() if self.url_2 else False
        self_url3 = str(self.url_3).strip() if self.url_3 else False
        for rec in self:
            url = str(rec.url_1).strip() if rec.url_1 else False
            if url:
                check = self.compute_url_validation(rec, self_url1)
                if check:
                    ur = False
                    cov_lst = str(check.mapped('name'))
                    raise ValidationError(_("Record matched at " + cov_lst))
        if self_url1 and self_url1 in [self_url2, self_url3]:
            raise ValidationError(_("You already have same URL in this record"))

    @api.onchange('url_2')
    def onchange_url_2_validation(self):
        self_url1 = str(self.url_1).strip() if self.url_1 else False
        self_url2 = str(self.url_2).strip() if self.url_2 else False
        self_url3 = str(self.url_3).strip() if self.url_3 else False
        for rec in self:
            url = str(rec.url_2).strip() if rec.url_2 else False
            if url:
                check = self.compute_url_validation(rec, self_url2)
                if check:
                    url = False
                    cov_lst = str(check.mapped('name'))
                    raise ValidationError(_("Record matched at " + cov_lst))
        if self_url2 and self_url2 in [self_url1, self_url3]:
            raise ValidationError(_("You already have same URL in this record"))

    @api.onchange('url_3')
    def onchange_url_3_validation(self):
        self_url1 = str(self.url_1).strip() if self.url_1 else False
        self_url2 = str(self.url_2).strip() if self.url_2 else False
        self_url3 = str(self.url_3).strip() if self.url_3 else False
        for rec in self:
            url = str(rec.url_3).strip() if rec.url_3 else False
            if url:
                check = self.compute_url_validation(rec, self_url3)
                if check:
                    url = False
                    cov_lst = str(check.mapped('name'))
                    raise ValidationError(_("Record matched at " + cov_lst))
        if self_url3 and self_url3 in [self_url2, self_url1]:
            raise ValidationError(_("You already have same URL in this record"))


class SubTaskURL(models.Model):
    _name = 'sub.task.url'

    digital_id = fields.Many2one('digital.videos')
    digital_seq = fields.Char('Sequence', related='digital_id.digital_seq', store=True)
    # task_id = fields.Many2one('project.task', required=True, domain="[('task_status', 'in', ['FB Videos' ,'Story']), " "('stage_id.is_closed', '=', False)]")
    task_id = fields.Many2one('project.task', required=True, domain="[('task_status', 'in', ['FB Videos' ,'Story']), ('parent_id', '=', False)]")
    task_tag_ids = fields.Many2many(
        'project.tags',
        'project_tags_sub_task_url_rel',
        'sub_task_url_id',
        'project_tags_id',
        related='task_id.tag_ids',
        string='Tags',
        store=True
    )
    task_seq = fields.Char(related="task_id.task_seq")
    parent_task_id = fields.Many2one('project.task', related='task_id.parent_id')
    project_id = fields.Many2one('project.project', related='task_id.project_id')
    is_spam = fields.Boolean(compute="compute_is_spam")
    start_time = fields.Datetime(string="Start")
    end_time = fields.Datetime(string="End")
    elapsed_time = fields.Char(compute="compute_start_end_time", string="Duration")
    agency_id = fields.Many2one('res.agency', string="Agency", related="digital_id.agency_id")

    @api.depends('start_time', 'end_time')
    def compute_start_end_time(self):
        for rec in self:
            rec.elapsed_time = False
            if rec.end_time:
                rec.elapsed_time = rec.end_time - rec.start_time

    def compute_is_spam(self):
        for rec in self:
            rec.is_spam = False
            if rec.digital_id:
                if rec.digital_id.is_spam:
                    rec.is_spam = True