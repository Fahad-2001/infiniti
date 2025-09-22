from odoo import fields, models, _


class MediaType(models.Model):
    _name = 'media.type'

    name = fields.Char(required=True)

    def open_digital_assets(self):
        digital_ids = self.env['digital.videos'].search([('media_type_id', '=', self._origin.id)]).ids
        return {
            'name': _('Digital Videos'),
            'view_mode': 'tree,form',
            'res_model': 'digital.videos',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', digital_ids)],
        }
