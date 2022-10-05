# -*- coding: utf-8 -*-

from odoo import models, fields, api


class list_formulas(models.Model):
    _name = "account.tax.repport.formulas.line"
    _description = "Formule"

    name = fields.Char('Nom')
    formula_id = fields.Many2one('account.tax.repport.formulas', 'Formule', ondelete='cascade')
    condition_id = fields.Many2one('account.tax.repport.formulas', 'Condition', ondelete='cascade')
    type = fields.Selection([
        ('cell', 'Valeur simple'),
        ('formula', 'Formule'),
    ],
        string="Operateur",
        required=True,
        default='cell')
    op = fields.Selection([
        ('plus', '+'),
        ('minus', '-'),
    ],
        string="Operateur",
        required=True,
        default='plus')
    range_from = fields.Integer('De')
    range_to = fields.Integer('A')
    code = fields.Integer('Code')

class list_formulas(models.Model):
    _name = "account.tax.repport.formulas"
    _description = "Formule"

    name = fields.Char(u'Nom')
    report_id = fields.Many2one('account.tax.repport', 'Rapport', ondelete='cascade')
    formula_line_ids = fields.One2many(comodel_name='account.tax.repport.formulas.line', inverse_name='formula_id',
                                  string=u'Formule')
    condition_ids = fields.One2many(comodel_name='account.tax.repport.formulas.line', inverse_name='condition_id',
                                  string=u'Condition')

class TaxRepport(models.Model):
    _name = 'account.tax.repport'

    name = fields.Char(u'Nom')
    cell = fields.Char(u'Cellule')
    code = fields.Integer(u'code')
    formula_ids = fields.One2many(comodel_name='account.tax.repport.formulas', inverse_name='report_id',
                                     string=u'Formule')
    type = fields.Selection([
        ('base', 'Base imposable (HT)'),
        ('tax', 'Taxe exigible'),
    ],required=False)

    cell_base = fields.Char(u'Cellule Base')
    cell_tax = fields.Char(u'Cellule Taxe')
    cell_prorata = fields.Char(u'Cellule Prorata')
    cell_calc_tax = fields.Char(u'Cellule Prorata X taxe')


    type_calcul = fields.Selection([
        ('manuel', 'Rempli manuellement'),
        ('auto', 'Calculé'),
    ], string='Type de calcul')


class AccountTax(models.Model):
    _inherit = 'account.tax'

    prorata = fields.Float('Prorata', default=100.0)


