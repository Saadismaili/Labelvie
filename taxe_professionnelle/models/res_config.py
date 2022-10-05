# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tp_rapport_excel = fields.Binary(string="Rapport Excel Taxe professionnelle")

    # @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            tp_rapport_excel=self.env['ir.config_parameter'].sudo().get_param('taxe_professionnelle.tp_rapport_excel'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        if self.tp_rapport_excel:
            self.env['ir.config_parameter'].sudo().set_param('taxe_professionnelle.tp_rapport_excel',
                                                             self.tp_rapport_excel)

