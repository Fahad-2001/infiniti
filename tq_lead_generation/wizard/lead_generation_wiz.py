from odoo import models, fields, api, _


class LeadGenerationWizard(models.Model):
    _name = 'lead.generation.wiz'

    platform_id = fields.Many2one('project.platform', string="Social Media Network")
    url = fields.Char(string="URL", required=True)

    def validate_url(self):
        url = str(self.url).strip()
        if url:
            lead_id = self.env['lead.generation'].search([('platform_id', '=', self.platform_id.id),('page_link', '=', url)])
            if lead_id:
                return self._action_open_record_form(lead_id[0])
            else:
                return self._action_open_new_form()

    def _action_open_new_form(self):
        return {
            "type": 'ir.actions.act_window',
            "res_model": 'lead.generation',
            'view_mode': 'form',
            "context": {
                **self.env.context,
                'active_id': self.id,
                'active_model': self._name,
                'default_platform_id': self.platform_id.id,
                'default_page_link': str(self.url).strip(),
            },
        }

    def _action_open_record_form(self, lead_id):
        return {
            "type": 'ir.actions.act_window',
            "res_model": 'lead.generation',
            'view_mode': 'form',
            'res_id': lead_id.id,
        }