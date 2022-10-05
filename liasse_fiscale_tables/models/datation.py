from odoo import models, fields, api, _ 

from lxml import etree
import base64
import zipfile

import os
directory = os.path.dirname(__file__)

class Datation(models.Model):
    _name = 'datation'
    
    name = fields.Char(string='Nom',default='DATATION ET EVENEMENTS POSTERIEURS')
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    date_clolure = fields.Datetime(string= 'Date de clôture')
    
    date_etablissement =  fields.Datetime(string='Date d\'établissement des états de synthèse ')
    
    description  = fields.Text()
    datation_ids = fields.One2many(comodel_name="datation.line", inverse_name="datation_id", string="II. EVENEMENTS NES POSTERIEUREMENT A LA CLOTURE DE L'EXERCICE NON RATTACHABLES A CET EXERCICE ET CONNUS AVANT LA 1ère COMMUNICATION EXTERNE DES ETAS DE SYNTHESE", required=False, copy=True )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('datation'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    
    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    def get_lines(self):
        pass

class DatationChild(models.Model):
    
    _name = 'datation.line'
    
    date  = fields.Datetime(string='Date')
    indication  = fields.Char(string='Indication des événements')
    datation_id = fields.Many2one(
        'datation',
        string='datation',
        )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('datation.line'))

    
    