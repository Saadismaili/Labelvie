# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LiassFiscal(models.Model):
    _name = 'liass.fiscal'

    name = fields.Char()
    line_ids = fields.One2many(string='Lignes',comodel_name='liass.fiscal.line',inverse_name='group_id' )

class LiassFiscalLine(models.Model):
    _name = 'liass.fiscal.line'
    _order = 'sequence asc'

    name = fields.Char(string = 'Nom')
    model = fields.Char(string = 'Model')
    sequence  = fields.Integer(string='sequence', required=True, )
    group_id = fields.Many2one(string='Group', comodel_name='liass.fiscal')
