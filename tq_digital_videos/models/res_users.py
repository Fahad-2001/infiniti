from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    user_role_id = fields.Many2one('user.access.role', string="User Role", required=False)
    notification_type = fields.Selection([
        ('email', 'Handle by Emails'),
        ('inbox', 'Handle in Odoo')],
        'Notification', required=True, default='inbox')

    @api.model
    def create(self, vals):
        if not vals.get('user_role_id'):
            default_role = self.env['user.access.role'].search([('name', '=', 'employee')], limit=1)
            if default_role:
                vals['user_role_id'] = default_role.id
        user = super().create(vals)
        user._assign_user_role_groups()
        return user

    def write(self, vals):
        res = super().write(vals)
        if 'user_role_id' in vals:
            self._assign_user_role_groups()
        return res

    def _assign_user_role_groups(self):
        for user in self:
            if user.user_role_id:
                user.groups_id = [(3, group.id) for group in user.user_role_id.group_ids_to_remove]
                user.groups_id = [(6, 0, user.user_role_id.group_ids.ids)]
                # if  user.user_role_id.menus_to_remove:
                #     user.hide_menu_ids = user.user_role_id.menus_to_remove.ids

