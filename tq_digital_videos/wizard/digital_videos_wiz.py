from odoo import models, fields, api, _


class DigitalVideosWizard(models.Model):
    _name = 'digital.videos.wiz'

    url = fields.Char(string="URL", required=True)

    def validate_url(self):
        url = str(self.url).strip()
        if url:
            digital_id = self.env['digital.videos'].search([('url_1', '=', url)])
            if not digital_id:
                digital_id = self.env['digital.videos'].search([('url_2', '=', url)])
            if not digital_id:
                digital_id = self.env['digital.videos'].search([('url_2', '=', url)])
            if digital_id:
                return self._action_open_record_form(digital_id[0])
            else:
                return self._action_open_new_form()

    def _action_open_new_form(self):
        return {
            "type": 'ir.actions.act_window',
            "res_model": 'digital.videos',
            'view_mode': 'form',
            "context": {
                **self.env.context,
                'active_id': self.id,
                'active_model': self._name,
                'default_url_1': str(self.url).strip(),
            },
        }

    def _action_open_record_form(self, digital_id):
        return {
            "type": 'ir.actions.act_window',
            "res_model": 'digital.videos',
            'view_mode': 'form',
            'res_id': digital_id.id,
        }