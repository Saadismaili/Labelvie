# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    honoraire_rapport_excel = fields.Binary(string="Rapport Excel Honoraires")

    # @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            honoraire_rapport_excel=self.env['ir.config_parameter'].sudo().get_param('honoraires.honoraire_rapport_excel'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        if self.honoraire_rapport_excel:
            self.env['ir.config_parameter'].sudo().set_param('honoraires.honoraire_rapport_excel',
                                                             self.honoraire_rapport_excel)
