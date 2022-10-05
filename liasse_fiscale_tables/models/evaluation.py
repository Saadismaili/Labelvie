from odoo import models, fields, api, _   
from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)
class Evaluation(models.Model):
    _name= 'evaluation'
    
    name = fields.Char(string='Nom', default='PRINCIPALES METHODES D\'EVALUATION SPECIFIQUES A L\'ENTREPRISE')
    
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    line_ids = fields.One2many(string='Lignes',comodel_name='evaluation.line',inverse_name='parent_id' )
    
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('evaluation'))
    @api.model
    def create(self, values):
        return super(Evaluation,self).create({
            'line_ids' : self.env['evaluation.line'].create([{'name':'I. ACTIF IMMOBILISE','parent_id':self.id,},
                                                                        {'name':'A. EVALUATION A L\'ENTREE','parent_id':self.id,},
                                                                        {'name':'1. Immobilisations en non-valeurs','parent_id':self.id,},
                                                                        {'name':'2. Immobilisations incorporelles','parent_id':self.id,},
                                                                        {'name':'3. Immobilisations corporelles','parent_id':self.id,},
                                                                        {'name':'4. Immobilisations financières','parent_id':self.id,},
                                                                        {'name':'B. CORRECTIONS DE VALEURS','parent_id':self.id,},
                                                                        {'name':'1. Méthodes d\'amortissements','parent_id':self.id,},
                                                                        {'name':'2. Méthodes de détermination des écarts de convertion-Actif','parent_id':self.id,},
                                                                        {'name':'3. Méthodes d’évaluation des provisions pour dépréciation','parent_id':self.id,},
                                                                        {'name':'II. ACTIF CIRCULANT (Hors trésorerie)','parent_id':self.id,},
                                                                        {'name':'A. EVALUATION A L\'ENTREE','parent_id':self.id,},
                                                                        {'name':'1. Stocks','parent_id':self.id,},
                                                                        {'name':'2. Créances','parent_id':self.id,},
                                                                        {'name':'3. Titres et valeurs de placement','parent_id':self.id,},
                                                                        {'name':'B. CORRECTIONS DE VALEUR','parent_id':self.id,},
                                                                        {'name':'1. Méthodes d\'évaluation des provisions pour dépréciation','parent_id':self.id,},
                                                                        {'name':'2. Méthodes de détermination des écarts de convertion-actif','parent_id':self.id,},
                                                                        {'name':'III. FINANCEMENT PERMANENT','parent_id':self.id,},
                                                                        {'name':'1. Méthodes de réévaluation','parent_id':self.id,},
                                                                        {'name':'2. Méthodes d\'évaluation des provisions réglementées','parent_id':self.id,},
                                                                        {'name':'3. Méthodes de détermination des écarts de convertion-Passif','parent_id':self.id,},
                                                                        {'name':'4. Dettes de financement permanent','parent_id':self.id,},
                                                                        {'name':'5. Méthodes d\'évaluation des provisions durables pour risques et charges','parent_id':self.id,},
                                                                        {'name':'VI. PASSIF CIRCULANT (Hors trésorerie)','parent_id':self.id,},
                                                                        {'name':'1. Dettes du passif circulant','parent_id':self.id,},
                                                                        {'name':'2. Méthodes d\'évaluation des autres provisions pour risques et charges','parent_id':self.id,},
                                                                        {'name':'3. Méthodes de détermination des écarts de convertion-Passif','parent_id':self.id,},
                                                                        {'name':'V. TRESORERIE','parent_id':self.id,},
                                                                        {'name':'1. Trésorerie - Actif','parent_id':self.id,},
                                                                        {'name':'2. Trésorerie - Passif','parent_id':self.id,},
                                                                        {'name':'3. Méthodes d\'évaluation des provisions pour dépréciation','parent_id':self.id,},
                                                                  ]),})
        
    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    def get_lines(self):
        pass
class EvaluationLines(models.Model):
    _name = 'evaluation.line'
    
    name = fields.Char(string=' ', readonly=True)
    text = fields.Char(string=' ')
    parent_id = fields.Many2one(
        'evaluation',
        string='Parent',
        )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('evaluation.line'))