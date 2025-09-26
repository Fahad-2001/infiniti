from odoo import fields,models,api, _
from odoo.exceptions import ValidationError, UserError


class ProjectTaskInherit(models.Model):
    _inherit = 'project.task'

    task_status = fields.Selection([('FB Videos', 'FB Videos'), ('Episode', 'Episode'), ('Story', 'Story'), ('Task', 'Task')])
    digital_video_ids = fields.One2many('sub.task.url', 'task_id')
    task_temp_id = fields.Many2one('task.template')
    task_seq = fields.Char('Name', readonly=True, default='New')
    task_type_id = fields.Many2one('task.type', string="Task Type")
    project_platform_id = fields.Many2one('project.platform', string="Project Platform")
    post_description = fields.Text()
    post_comment_ids = fields.One2many('post.comment', 'task_id')
    is_click_task_temp = fields.Boolean()
    calendar_id = fields.Many2one('calendar.event')
    calendar_date = fields.Datetime()
    calendar_status_id = fields.Many2one('calendar.status')
    order_number = fields.Char()
    commercial_partner_id = fields.Many2one(related="partner_id.commercial_partner_id")
    email_from = fields.Char('Email From')
    email_cc = fields.Char('Email cc')
    display_project_id = fields.Many2one('project.project')
    project_tag_ids = fields.Many2many(
        'project.tags',
        'project_task_project_tags_rel',  # unique relation table name
        'task_id',                       # column referring to this model
        'tag_id',                        # column referring to the related model
        related="project_id.tag_ids",
        string="Project Tags",
        store=True
    )

    def write(self, values):
        for rec in self:
            if 'active' in values and not values['active']:
                for line in rec.child_ids:
                    line.active = False
            if 'active' in values and values['active']:
                child_ids = self.env['project.task'].search([('parent_id', '=', rec.id), ('active', '=' , False)])
                for line in child_ids:
                    line.active = True
        return super(ProjectTaskInherit, self).write(values)

    def get_project_tags(self):
        for rec in self:
            print("Project Tags ---->>", rec.project_id.tag_ids)
            if rec.project_id.tag_ids:
                rec.project_tag_ids = [(6, 0, rec.project_id.tag_ids.ids)]

    def assign_tags_to_project(self):
        projects = self.env['project.project'].sudo().search([('tag_ids', '!=', False)])
        for project in projects:
            print("Project Tasks Ids ---->>", project.tag_ids)
            project.task_ids.write({'project_tag_ids': [(6, 0, project.tag_ids.ids)]})

    _sql_constraints = [
        ('order_number_uniq', 'UNIQUE (order_number)', 'Order Number must be Unique')
    ]

    @api.onchange('calendar_status_id')
    def update_calendar_status(self):
        for rec in self:
            if rec.calendar_id:
                rec.calendar_id.status_id = rec.calendar_status_id.id

    def unlink(self):
        for rec in self:
            if rec.child_ids:
                raise ValidationError(_("You have to delete Sub Tasks first!"))
        return super(ProjectTaskInherit, self).unlink()

    @api.onchange('project_id', 'display_project_id')
    def on_change_all_tasks_project(self):
        for rec in self:
            for line in rec.child_ids:
                line.display_project_id = rec.project_id.id
                line.display_project_id = rec.project_id.id


    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        domain = args or []
        domain += ["|", ("name", operator, name), ("task_seq", operator, name)]
        return self.search(domain, limit=limit).name_get()

    @api.model
    def create(self, vals):
        if vals.get('task_seq', 'New') == 'New':
            vals['task_seq'] = self.env['ir.sequence'].next_by_code('project.task.seq') or '/'
        res = super(ProjectTaskInherit , self).create(vals)
        return res

    def fetch_task_from_template(self):
        for rec in self:
            if rec.task_temp_id:
                for line in rec.task_temp_id.subtask_ids:
                    vals = {
                        'name': line.name,
                        'parent_id': rec.id,
                        'project_id': rec.project_id.id,
                        'display_project_id': rec.display_project_id.id,
                        'stage_id': self.env['project.task.type'].search([], order="sequence")[0].id
                    }
                    task_create = self.env['project.task'].sudo().create(vals)
                rec.is_click_task_temp = True

    def action_view_tasks(self):
        subtasks = self.env['project.task'].search([('parent_id', '=', self.id)]).ids
        print("Sub task ---->>", subtasks)
        if subtasks:
            action = self.with_context(active_id=self.id, active_ids=subtasks).env.ref('tq_digital_videos.act_project_project_2_project_task_all_new').sudo().read()[0]
            action['display_name'] = self.name
        else:
            return {
                "type": 'ir.actions.act_window',
                "res_model": 'project.task',
                'view_mode': 'form',
                'res_id': self.id
            }
        return action

    def get_sequnce_list(self):
        for rec in self:
            if rec.digital_video_ids:
                sequence = rec.digital_video_ids.mapped("digital_seq")
                quoted_elements = ['"{}"'.format(elem) for elem in sequence]
                output_string = ' '.join(quoted_elements)
                raise UserError(output_string)


class PostComment(models.Model):
    _name = 'post.comment'

    post_comment = fields.Text(string="Comment")
    post_comment_user_id = fields.Many2one('res.users', readonly=True, string="User", default=lambda self: self.env.user)
    post_comment_datetime = fields.Datetime(string="Date", readonly=True, default=lambda self: fields.Datetime.now())
    post_comment_posted = fields.Boolean(string="Posted")
    task_id = fields.Many2one('project.task')