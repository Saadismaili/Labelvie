from odoo import models, fields, api, _   

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)

class Suretes(models.Model):
    _name = 'suretes'
    
    name = fields.Char(string='Nom', default='SURETES REELLES DONNEES OU RECUES')
    
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    line_1_ids = fields.One2many(string='Lignes',comodel_name='suretes.line1',inverse_name='parent_id' )
    line_2_ids = fields.One2many(string='Lignes',comodel_name='suretes.line2',inverse_name='parent_id' )
    
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('suretes'))
    
    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    def get_lines(self):
        pass
class SuretesLine1(models.Model):
    _name = "suretes.line1"
    
    name = fields.Char(string='TIERS CREDITEURS OU TIERS DEBITEURS')
    
    amount_convert = fields.Float(string='Montant couvert par la sûreté')
    nature = fields.Char(string='Nature')
    date = fields.Datetime(string='Date  lieu d\'inscription')
    objet = fields.Char(string='Objet')
    value = fields.Char(string='Valeur comptable de la sûreté donnée à la date de clôture')

    parent_id = fields.Many2one(
        'suretes',
        string='Parent',
        )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('suretes.line1'))

class SuretesLine2(models.Model):
    _name = "suretes.line2"
    
    name = fields.Char(string='TIERS CREDITEURS OU TIERS DEBITEURS')
    
    amount_convert = fields.Float(string='Montant couvert par la sûreté')
    nature = fields.Char(string='Nature')
    date = fields.Datetime(string='Date  lieu d\'inscription')
    objet = fields.Char(string='Objet')
    value = fields.Char(string='Valeur comptable de la sûreté donnée à la date de clôture')
    parent_id = fields.Many2one(
        'suretes',
        string='Parent',
        )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('suretes.line2'))
  