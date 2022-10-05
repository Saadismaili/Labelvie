# -*- coding: utf-8 -*-

from odoo import fields, models

class account_asset(models.Model):
    _inherit = "account.asset.asset"

    n_titre_foncier = fields.Char(string=u"N° du titre foncier ou de la réquisition", required=False)
    superficie = fields.Float(string=u"Superficie en m²",  required=False, )
    statut = fields.Char(string=u"Statut patrimonial du bien (propriété,location ou autre…)", required=False, )
    type_acquisition = fields.Selection(string="Etat", selection=[('n', 'Neuf(N)'), ('o', 'Occasion(O)')], required=False, )