from odoo import models, fields, api, _   

from lxml import etree
import base64
import zipfile

import os
directory = os.path.dirname(__file__)

class Changement(models.Model):
    _name = 'changement'
    
    name = fields.Char(string='Nom', default='ETAT DES CHANGEMENTS DE METHODES')
    
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    line_1_ids = fields.One2many(string='Lignes',comodel_name='changement.line1',inverse_name='parent_id' )
    line_2_ids = fields.One2many(string='Lignes',comodel_name='changement.line2',inverse_name='parent_id' )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('changement'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    
    
    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    def get_lines(self):
        pass
class ChangementLine1(models.Model):
    _name = "changement.line1"
    
    name = fields.Char(string='Nom')
    justification = fields.Char(string='JUSTIFICATIONS DES DEROGATIONS')
    influence = fields.Char(string='INFLUENCE DES DEROGATIONS SUR LE PATRIMOINE, LA SITUATION FINANCIERE ET LES RESULTATS')
    parent_id = fields.Many2one(
        'changement',
        string='Parent',
        )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('changement.line1'))

class ChangementLine2(models.Model):
    _name = "changement.line2"
    
    name = fields.Char(string='Nom')
    justification = fields.Char(string='JUSTIFICATIONS DES DEROGATIONS')
    influence = fields.Char(string='INFLUENCE DES DEROGATIONS SUR LE PATRIMOINE, LA SITUATION FINANCIERE ET LES RESULTATS')
    parent_id = fields.Many2one(
        'changement',
        string='Parent',
        )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('changement.line2'))
  