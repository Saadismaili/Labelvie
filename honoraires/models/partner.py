# -*- coding: utf-8 -*-

from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    honoraire = fields.Boolean(string='Honoraires', default=False)