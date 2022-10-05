# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    compute_type = fields.Selection([('simple', u'Simple'),
                                     ('calculee', u'Calculé')], string='Type de Calcul', default='calculee')
    product_type_id = fields.One2many('product.type', 'product_id', string='Type')


class ProductType(models.Model):
    _name = "product.type"

    name = fields.Char('Nom', required=True)
    product_id = fields.Many2one('product.template', string='Article', invisible=True)

