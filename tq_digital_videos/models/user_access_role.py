from odoo import models, fields

class UserAccessRole(models.Model):
    _name = "user.access.role"
    _description = "Users Access Role"
    _rec_name = "rec_name"

    rec_name = fields.Char("Name")
    name = fields.Selection([
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('hr', 'HR'),
        ('admin', 'Admin'),
    ], required=True, default='employee', string="Role Type")

    group_ids = fields.Many2many('res.groups', 'user_access_role_groups_rel', 'role_id', 'group_id',string='Groups', required=True)
    group_ids_to_remove = fields.Many2many('res.groups', 'user_access_role_groups_to_remove_rel', 'role_id', 'group_id', string='Groups To Remove', required=False)
    # menus_to_remove = fields.Many2many('ir.ui.menu', string="Menus to Hide")

    def write(self, vals):
        print("Access role Vals ====>>>", vals)
        res = super(UserAccessRole, self).write(vals)
        for rec in self:
            res_users = self.env['res.users'].search([('user_role_id.rec_name', '=', self.rec_name)])
            res_users.groups_id = [(3, group.id) for group in rec.group_ids_to_remove]
            res_users.groups_id = [(6, 0, rec.group_ids.ids)]
            print("Res userrss ====", len(res_users))
        return res
