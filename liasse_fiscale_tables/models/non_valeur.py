from odoo import models, fields, api, _

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)

class NonValeur(models.Model):
    
    _name = 'preliminaire'
    
    name = fields.Char(string='Nom')
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    line_ids = fields.One2many(comodel_name="preliminaire.line", inverse_name="parent_id", string="Lignes", required=False, copy=True )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('preliminaire'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    
    def get_lines(self):
        """This Function calculates balance and generate lines from account.move.line that containg the rebrique 21"""
        line = []
        for rec in self:
            rec.line_ids = [(5,0,0)]
            
            moves = self.env['account.move.line'].search([('account_id.code','=like','21%'),('company_id','=',self.env.company.id)])
            for move in moves:
                if move.date.year <= rec.fy_n_id.date_end.year and move.move_id.state == 'posted' : 
                    line = self.env['preliminaire.line'].search([('code','=',move.account_id.code),('parent_id','=',rec.id)]) 
                    if line.exists():
                        line.write({
                            'amount' : line.amount + move.debit - move.credit
                        })
                    else:                            
                        self.env['preliminaire.line'].create({
                            'code':move.account_id.code,
                            'intitule':move.name,
                            'amount':move.debit - move.credit,
                            'parent_id': rec.id 
                        })
    
    
    
class NonValeurLine(models.Model):
    _name = 'preliminaire.line'
    
    code = fields.Char(string='Compte principale')    
    intitule = fields.Char(string='INTITULE')    
    amount = fields.Float(string='MONTANT') 
    parent_id = fields.Many2one(
    comodel_name='preliminaire'
    ,string = 'Parent'
    ) 
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('preliminaire.line'))  