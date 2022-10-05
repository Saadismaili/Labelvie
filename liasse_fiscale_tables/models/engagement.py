from odoo import models, fields, api, _ 
from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)  

class Engagement(models.Model):
    _name = 'engagement'
    
    name = fields.Char(string='Nom', default='ENGAGEMENTS FINANCIERS')
    
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    line_1_ids = fields.One2many(string='Lignes',comodel_name='engagement.line1',inverse_name='parent_id' )
    line_2_ids = fields.One2many(string='Lignes',comodel_name='engagement.line2',inverse_name='parent_id' )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('engagement'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    
    @api.model
    def create(self, values):
        return super(Engagement,self).create({
            'fy_n_id':self.fy_n_id.id,
            'line_1_ids' : self.env['engagement.line1'].create([{'name':'- Avals et cautions','parent_id':self.id,},
                                                                  {'name':'- Engagements en matière de pensions de retraites et obligations similaires','parent_id':self.id,},
                                                                  {'name':'- Autres engagements donnés','parent_id':self.id,},
                                                                  ]),
            'line_2_ids' : self.env['engagement.line2'].create([{'name':'- Avals et cautions','parent_id':self.id,},
                                                                  {'name':'- Autres engagements reçus','parent_id':self.id,},
                                                                  ]),
        })
        
    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    def get_lines(self):
        pass
class EngagementLine1(models.Model):
    _name = "engagement.line1"
    
    name = fields.Char(string='Nom')
    current_amount = fields.Float(string='Montants exercice')
    previous_amount = fields.Float(string='Montants exercice précédent')
    parent_id = fields.Many2one(
        'engagement',
        string='Parent',
        )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('engagement.line1'))

class EngagementLine2(models.Model):
    _name = "engagement.line2"
    
    name = fields.Char(string='Nom')
    current_amount = fields.Float(string='Montants exercice')
    previous_amount = fields.Float(string='Montants exercice précédent')
    parent_id = fields.Many2one(
        'engagement',
        string='Parent',
        )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('engagement.line2'))
  