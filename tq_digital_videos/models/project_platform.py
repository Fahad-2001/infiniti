from odoo import fields, models, _
from odoo.exceptions import UserError
import ast

class ProjectPlatform(models.Model):
    _name = 'project.platform'

    name = fields.Char(required=True)


class ProjectPlatformLink(models.Model):
    _name = 'project.platform.link'

    platform_id = fields.Many2one('project.platform', required=True, string="Platform")
    project_id = fields.Many2one('project.project')


class ProjectProjectInherit(models.Model):
    _inherit = 'project.project'

    platform_ids = fields.One2many('project.platform.link', 'project_id', string="Project Platform")

    def action_view_tasks(self):
        user = self.env.user
        updated_domain = []
        action = self.env['ir.actions.act_window'].with_context({'active_id': self.id})._for_xml_id('project.act_project_project_2_project_task_all')
        action['display_name'] = _("%(name)s", name=self.name)
        context = action['context'].replace('active_id', str(self.id))
        context = ast.literal_eval(context)
        print(user.has_group('project.group_project_user'), 'IFFF and', user.has_group('tq_digital_videos.project_task_group_user'))
        if user.has_group('project.group_project_user') and user.has_group('tq_digital_videos.project_task_group_user'):
            updated_domain.extend([('project_id', '=', self.id), ('parent_id', '=', False), ('user_ids', '=', user.id)])
            action['domain'] = updated_domain
        elif user.has_group('project.group_project_manager') or user.has_group('tq_digital_videos.project_task_group_manager_qc') or user.has_group('tq_digital_videos.project_task_group_manager'):
            print(user.has_group('project.group_project_manager'), 'or', user.has_group('tq_digital_videos.project_task_group_manager_qc'), 'or', user.has_group('tq_digital_videos.project_task_group_manager'))
            updated_domain.extend([('project_id', '=', self.id), ('parent_id', '=', False)])
            action['domain'] = updated_domain
        print("Updated Domain --->>>", updated_domain)
        context.update({
            'create': self.active,
            'active_test': self.active
        })
        action['context'] = context
        return action


class ProjectTask(models.Model):
    _inherit = 'project.task'

    user_ids = fields.Many2many('res.users', default=lambda self: self.env.user)
