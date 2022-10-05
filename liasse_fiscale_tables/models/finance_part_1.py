# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)


class FinanceFirst(models.Model):
    _name = 'finance.first'
    _description = 'TABLEAU DE Finance'

    name = fields.Char(string=u"Nom",default="TABLEAU DE FINANCE",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    line_ids = fields.One2many(comodel_name="finance.first.line", inverse_name="parent_id", string="Lignes", required=False, copy=True )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('finance.first'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    @api.model
    def create(self, values):
        return super(FinanceFirst,self).create({
            'fy_n_id':self.fy_n_id.id,
            'line_ids' : self.env['finance.first.line'].create([{'name':'1- Financement permanent','edi_montant_debut':14113,'edi_montant_fin':14120,'edi_p_debit_fin':14127,'edi_n_debit_fin':14134,'parent_id':self.id,},
                                                                        {'name':'2- Moins actif immobilisé','edi_montant_debut':14114,'edi_montant_fin':14121,'edi_p_debit_fin':14128,'edi_n_debit_fin':14135,'parent_id':self.id,},
                                                                        {'name':'3- FONDS DE ROULEMENT FONCTIONNEL (1 - 2) (A)','edi_montant_debut':14115,'edi_montant_fin':14122,'edi_p_debit_fin':14129,'edi_n_debit_fin':14136,'parent_id':self.id,},
                                                                        {'name':'4- Actif circulant','parent_id':self.id,'edi_montant_debut':14116,'edi_montant_fin':14123,'edi_p_debit_fin':14130,'edi_n_debit_fin':14137,},
                                                                        {'name':'5- Moins passif circulant','parent_id':self.id,'edi_montant_debut':14117,'edi_montant_fin':14124,'edi_p_debit_fin':14131,'edi_n_debit_fin':14138,},
                                                                        {'name':'6- BESOIN DE FINANCEMENT GLOBAL (4 - 5) (B)','edi_montant_debut':14118,'edi_montant_fin':14125,'edi_p_debit_fin':14132,'edi_n_debit_fin':14139,'parent_id':self.id,},
                                                                        {'name':'7- TRESORERIE NETTE (ACTIF - PASSIF) = A - B','edi_montant_debut':14119,'edi_montant_fin':14126,'edi_p_debit_fin':14133,'edi_n_debit_fin':14140,'parent_id':self.id,},
                                                                  ]),})

    def from_string_to_list(self,val,list):
        list = []
        for x in str(val):
            list.append(x)
        return list
    
    def list_verification(self,list1,list2):
        if len(list1) == 2:
            if list1[0] == list2[0] and list1[1] == list2[1]:
                return True
        elif len(list1) == 3:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2]:
                return True
        elif len(list1) == 4:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2] and list1[3] == list2[3] :
                return True
        elif len(list1) == 5:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2] and list1[3] == list2[3] and list1[4] == list2[4]:
                return True
        else:
            return False

    def bal_calulator_previous_years(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                for entry in journal_entries:
                    if rec.fy_n_id:
                        for ref in rec.fy_n_id:
                            for item in entry.line_ids:
                                if ref.date_end.year > entry.date.year:
                                    item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                    col = rec.from_string_to_list(code,col)
                                    if rec.list_verification(col,item_code):
                                        if str(item_code[0] +item_code[1]) == '51' or  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '7119' or  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '7129':
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '2' and str(item_code[0] +item_code[1]) != '28' and str(item_code[0] +item_code[1]) != '29' :
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '3' and str(item_code[0] +item_code[1]) != '39':
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '6' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '6119' and  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '6129':
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '1' or item_code[0] == '4' or str(item_code[0] +item_code[1]) == '55' or str(item_code[0] +item_code[1]) == '59':
                                            bal += item.credit - item.debit
                                        elif  item_code[0] == '7' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '7119' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '7129' :
                                            bal += item.credit - item.debit 
                                        elif   str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '6119' or str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '6129' or str(item_code[0] +item_code[1]) == '28' or str(item_code[0] +item_code[1]) == '29' or str(item_code[0] +item_code[1]) == '39' :
                                            bal += item.credit - item.debit 
            return bal
    
    def bal_calulator_current_year(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                for entry in journal_entries:
                    if rec.fy_n_id:
                        for ref in rec.fy_n_id:
                            for item in entry.line_ids:
                                if ref.date_end.year >= entry.date.year:
                                    item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                    col = rec.from_string_to_list(code,col)
                                    if rec.list_verification(col,item_code):
                                        if str(item_code[0] +item_code[1]) == '51' or  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '7119' or  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '7129':
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '2' and str(item_code[0] +item_code[1]) != '28' and str(item_code[0] +item_code[1]) != '29' :
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '3' and str(item_code[0] +item_code[1]) != '39':
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '6' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '6119' and  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '6129':
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '1' or item_code[0] == '4' or str(item_code[0] +item_code[1]) == '55' or str(item_code[0] +item_code[1]) == '59':
                                            bal += item.credit - item.debit
                                        elif  item_code[0] == '7' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '7119' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '7129' :
                                            bal += item.credit - item.debit   
                                        elif   str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '6119' or str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '6129' or str(item_code[0] +item_code[1]) == '28' or str(item_code[0] +item_code[1]) == '29' or str(item_code[0] +item_code[1]) == '39' :
                                            bal += item.credit - item.debit                                         
            return bal
    
    def bal_calulator_net_prev(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                for entry in journal_entries:
                    if rec.fy_n_id:
                        for ref in rec.fy_n_id:
                            for item in entry.line_ids:
                                if ref.date_end.year -1 == entry.date.year:
                                    item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                    col = rec.from_string_to_list(code,col)
                                    if rec.list_verification(col,item_code):
                                        if str(item_code[0] +item_code[1]) == '51' or  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '7119' or  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '7129':
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '2' and str(item_code[0] +item_code[1]) != '28' and str(item_code[0] +item_code[1]) != '29' :
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '3' and str(item_code[0] +item_code[1]) != '39':
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '6' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '6119' and  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '6129':
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '1' or item_code[0] == '4' or str(item_code[0] +item_code[1]) == '55' or str(item_code[0] +item_code[1]) == '59':
                                            bal += item.credit - item.debit
                                        elif  item_code[0] == '7' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '7119' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '7129' :
                                            bal += item.credit - item.debit 
                                        elif   str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '6119' or str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '6129' or str(item_code[0] +item_code[1]) == '28' or str(item_code[0] +item_code[1]) == '29' or str(item_code[0] +item_code[1]) == '39' :
                                            bal += item.credit - item.debit 
            return bal
    
    def bal_calulator_net_year(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                for entry in journal_entries:
                    if rec.fy_n_id:
                        for ref in rec.fy_n_id:
                            for item in entry.line_ids:
                                if ref.date_end.year == entry.date.year:
                                    item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                    col = rec.from_string_to_list(code,col)
                                    if rec.list_verification(col,item_code):
                                        if str(item_code[0] +item_code[1]) == '51' or  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '7119' or  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '7129':
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '2' and str(item_code[0] +item_code[1]) != '28' and str(item_code[0] +item_code[1]) != '29' :
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '3' and str(item_code[0] +item_code[1]) != '39':
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '6' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '6119' and  str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '6129':
                                            bal += item.debit - item.credit
                                        elif item_code[0] == '1' or item_code[0] == '4' or str(item_code[0] +item_code[1]) == '55' or str(item_code[0] +item_code[1]) == '59':
                                            bal += item.credit - item.debit
                                        elif  item_code[0] == '7' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '7119' and str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) != '7129' :
                                            bal += item.credit - item.debit   
                                        elif   str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '6119' or str(item_code[0] +item_code[1] +item_code[2] +item_code[3]) == '6129' or str(item_code[0] +item_code[1]) == '28' or str(item_code[0] +item_code[1]) == '29' or str(item_code[0] +item_code[1]) == '39' :
                                            bal += item.credit - item.debit                                         
            return bal
                
    def get_lines(self):
        for rec in self:
            line_1 = self.env['finance.first.line'].search([('parent_id','=',rec.id),('name','=','1- Financement permanent')])
            line_1.write({
                'montant_debut':abs(self.bal_calulator_current_year(['172','171','155','151','148','141','135','131','118','116','115','114','113','112','1119','1111']) + (self.bal_calulator_net_year(['71','73','75']) - self.bal_calulator_net_year(['61','63','65','67']))),
                'montant_fin':abs(self.bal_calulator_previous_years(['172','171','155','151','148','141','135','131','118','116','115','114','113','112','1119','1111']) +  self.bal_calulator_net_prev(['71','73','75']) - self.bal_calulator_net_prev(['61','63','65','67'])),
                'p_debit_fin':line_1.montant_debut - line_1.montant_fin if line_1.montant_debut - line_1.montant_fin < 0 else 0,
                'n_debit_fin':abs(line_1.montant_debut - line_1.montant_fin) if line_1.montant_debut - line_1.montant_fin > 0 else 0,
            })
            line_2 = self.env['finance.first.line'].search([('parent_id','=',rec.id),('name','=','2- Moins actif immobilisé')])
            line_2.write({
                'montant_debut':abs(self.bal_calulator_current_year(['21','22','23','24','27']) - self.bal_calulator_current_year(['28'])),
                'montant_fin':abs(self.bal_calulator_previous_years(['21','22','23','24','27']) - self.bal_calulator_previous_years(['28'])),
                'p_debit_fin':line_2.montant_debut - line_2.montant_fin if line_2.montant_debut - line_2.montant_fin > 0 else 0,
                'n_debit_fin':abs(line_2.montant_debut - line_2.montant_fin) if line_2.montant_debut - line_2.montant_fin < 0 else 0,
            })
            line_3 = self.env['finance.first.line'].search([('parent_id','=',rec.id),('name','=','3- FONDS DE ROULEMENT FONCTIONNEL (1 - 2) (A)')])
            line_3.write({
                'montant_debut':line_1.montant_debut - line_2.montant_debut,
                'montant_fin':line_1.montant_fin - line_2.montant_fin,
                'p_debit_fin':line_3.montant_debut - line_3.montant_fin if line_3.montant_debut - line_3.montant_fin < 0 else 0,
                'n_debit_fin':abs(line_3.montant_debut - line_3.montant_fin) if line_3.montant_debut - line_3.montant_fin > 0 else 0,
            })
            line_4 = self.env['finance.first.line'].search([('parent_id','=',rec.id),('name','=','4- Actif circulant')])
            line_4.write({
                'montant_debut':abs(self.bal_calulator_current_year(['31','34','35','37'])),
                'montant_fin':abs(self.bal_calulator_previous_years(['31','34','35','37'])),
                'p_debit_fin':line_4.montant_debut - line_4.montant_fin if line_4.montant_debut - line_4.montant_fin > 0 else 0,
                'n_debit_fin':abs(line_4.montant_debut - line_4.montant_fin) if line_4.montant_debut - line_4.montant_fin < 0 else 0,
            })
            line_5 = self.env['finance.first.line'].search([('parent_id','=',rec.id),('name','=','5- Moins passif circulant')])
            line_5.write({
                'montant_debut':abs(self.bal_calulator_current_year(['44','45','47'])),
                'montant_fin':abs(self.bal_calulator_previous_years(['44','45','47'])),
                'p_debit_fin':line_5.montant_debut - line_5.montant_fin if line_5.montant_debut - line_5.montant_fin < 0 else 0,
                'n_debit_fin':abs(line_5.montant_debut - line_5.montant_fin) if line_5.montant_debut - line_5.montant_fin > 0 else 0,
            })
            line_6 = self.env['finance.first.line'].search([('parent_id','=',rec.id),('name','=','6- BESOIN DE FINANCEMENT GLOBAL (4 - 5) (B)')])
            line_6.write({
                'montant_debut':abs(self.bal_calulator_current_year(['31','34','35','37']) - self.bal_calulator_current_year(['44','45','47'])),
                'montant_fin':abs(self.bal_calulator_previous_years(['31','34','35','37']) - self.bal_calulator_previous_years(['44','45','47'])),
                'p_debit_fin':line_6.montant_debut - line_6.montant_fin if line_6.montant_debut - line_6.montant_fin > 0 else 0,
                'n_debit_fin':abs(line_6.montant_debut - line_6.montant_fin) if line_6.montant_debut - line_6.montant_fin < 0 else 0,
            })
            line_7 = self.env['finance.first.line'].search([('parent_id','=',rec.id),('name','=','7- TRESORERIE NETTE (ACTIF - PASSIF) = A - B')])
            line_7.write({
                'montant_debut':line_3.montant_debut - line_6.montant_debut,
                'montant_fin':line_3.montant_fin - line_6.montant_fin,
                'p_debit_fin':line_7.montant_debut - line_7.montant_fin if line_7.montant_debut - line_7.montant_fin > 0 else 0,
                'n_debit_fin':abs(line_7.montant_debut - line_7.montant_fin) if line_7.montant_debut - line_7.montant_fin < 0 else 0,
            })

    def get_xml(self,parent):
        pass
    
class FinanceFirstLine(models.Model):
    _name = 'finance.first.line' 
    _description = 'LIGNES TABLEAU DE FINANCE'

    name = fields.Char(string=u"I- SYNTHESE DES MASSES DU BILAN",required=True,readonly=True)
    montant_debut = fields.Float(string=u"EXERCICE (a)",  required=False,readonly=True )
    montant_fin = fields.Float(string=u"EXERCICE PRECEDENT (b)",  required=False, readonly=True )
    p_debit_fin = fields.Float(string=u"VARIATION (a - b) EMPLOIS (C)",  required=False, readonly=True )
    n_debit_fin = fields.Float(string=u"VARIATION (a - b) RESSOURCES (D)",  required=False, readonly=True )
    
    # Code edi
    edi_montant_debut = fields.Integer(string=u"EXERCICE (a)",  required=False,readonly=True )
    edi_montant_fin = fields.Integer(string=u"EXERCICE PRECEDENT (b)",  required=False, readonly=True )
    edi_p_debit_fin = fields.Integer(string=u"VARIATION (a - b) EMPLOIS (C)",  required=False, readonly=True )
    edi_n_debit_fin = fields.Integer(string=u"VARIATION (a - b) RESSOURCES (D)",  required=False, readonly=True )
    
    # Relational Fields
    parent_id = fields.Many2one(comodel_name="finance.first", string="finance", required=False, readonly=True  )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('finance.first.line'))