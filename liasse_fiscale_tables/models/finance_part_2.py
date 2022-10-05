# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)


class FinanceSecond(models.Model):
    _name = 'finance.second'
    # _inherit = 'methods'
    _description = 'TABLEAU DE Finance'

    name = fields.Char(string=u"Nom",default="TABLEAU DE FINANCE",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    line_ids = fields.One2many(comodel_name="finance.second.line", inverse_name="parent_id", string="Lignes", required=False, copy=True )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('finance.second'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    @api.model
    def create(self, values):
        return super(FinanceSecond,self).create({
            'fy_n_id':self.fy_n_id.id,
            'line_ids' : self.env['finance.second.line'].create([{'name':'* AUTOFINANCEMENT (A)','edi_emploi_debut':14172,'edi_ressource_debut':14184,'edi_emploi_fin':14196,'edi_ressource_fin':14208,'parent_id':self.id,},
                                                                    {'name':'- Capacité d\'autofinancement','edi_emploi_debut':14173,'edi_ressource_debut':14185,'edi_emploi_fin':14197,'edi_ressource_fin':14209,'parent_id':self.id,},
                                                                    {'name':'- Distribution de bénéfices','edi_emploi_debut':14174,'edi_ressource_debut':14186,'edi_emploi_fin':14198,'edi_ressource_fin':14210,'parent_id':self.id,},
                                                                    {'name':'* CESSIONS ET REDUCTIONS D\'IMMOBILISATIONS (B)','edi_emploi_debut':14175,'edi_ressource_debut':14187,'edi_emploi_fin':14199,'edi_ressource_fin':14211,'parent_id':self.id,},
                                                                    {'name':'- Cessions d\'immobilisations incorporelles','edi_emploi_debut':14176,'edi_ressource_debut':14188,'edi_emploi_fin':14200,'edi_ressource_fin':14212,'parent_id':self.id,},
                                                                    {'name':'- Cessions d\'immobilisations corporelles','edi_emploi_debut':14177,'edi_ressource_debut':14189,'edi_emploi_fin':14201,'edi_ressource_fin':14213,'parent_id':self.id,},
                                                                    {'name':'- Cessions d\'immobilisations financières','edi_emploi_debut':14178,'edi_ressource_debut':14190,'edi_emploi_fin':14202,'edi_ressource_fin':14214,'parent_id':self.id,},
                                                                    {'name':'- Récupérations sur créances immobilisées','edi_emploi_debut':14179,'edi_ressource_debut':14191,'edi_emploi_fin':14203,'edi_ressource_fin':14215,'parent_id':self.id,},
                                                                    {'name':'* AUGEMENTATION DES CAPITAUX PROPRES ET ASSIMILES (C)','edi_emploi_debut':14180,'edi_ressource_debut':14192,'edi_emploi_fin':14204,'edi_ressource_fin':14216,'parent_id':self.id,},
                                                                    {'name':'- Augmentations de capital, apports','edi_emploi_debut':14181,'edi_ressource_debut':14193,'edi_emploi_fin':14205,'edi_ressource_fin':14217,'parent_id':self.id,},
                                                                    {'name':'- Subventions d\'investissement','edi_emploi_debut':14182,'edi_ressource_debut':14194,'edi_emploi_fin':14206,'edi_ressource_fin':14218,'parent_id':self.id,},
                                                                    {'name':'* AUGMENTATION DES DETTES DE FINANCEMENT (D) (nettes des primes de remboursements)','edi_emploi_debut':14183,'edi_ressource_debut':14195,'edi_emploi_fin':14207,'edi_ressource_fin':14219,'parent_id':self.id,},
                                                                    {'name':'TOTAL I- RESSOURCES STABLES (A+B+C+D)','edi_emploi_debut':14221,'edi_ressource_debut':14222,'edi_emploi_fin':14223,'edi_ressource_fin':14224,'parent_id':self.id,},
                                                                    {'name':'II- EMPLOIS ET RESSOURCES- II- EMPLOIS STABLES DE L\'EXERCICE (FLUX)','parent_id':self.id,},
                                                                    {'name':'* ACQUISITIONS ET AUGEMENTATIONS D\'IMMOBILISATIONS (E)','edi_emploi_debut':14233,'edi_ressource_debut':14241,'edi_emploi_fin':14249,'edi_ressource_fin':14257,'parent_id':self.id,},
                                                                    {'name':'- Acquisitions d\'immobilisations incorporelles','edi_emploi_debut':14234,'edi_ressource_debut':14242,'edi_emploi_fin':14250,'edi_ressource_fin':14258,'parent_id':self.id,},
                                                                    {'name':'- Acquisitions d\'immobilisations corporelles','edi_emploi_debut':14235,'edi_ressource_debut':14243,'edi_emploi_fin':14251,'edi_ressource_fin':14259,'parent_id':self.id,},
                                                                    {'name':'- Acquisitions d\'immobilisations financières','edi_emploi_debut':14236,'edi_ressource_debut':14244,'edi_emploi_fin':14252,'edi_ressource_fin':14260,'parent_id':self.id,},
                                                                    {'name':'- Augmentation des créances immobilisées','edi_emploi_debut':14237,'edi_ressource_debut':14245,'edi_emploi_fin':14253,'edi_ressource_fin':14261,'parent_id':self.id,},
                                                                    {'name':'* REMBOURSEMENT DES CAPITAUX PROPRES (F)','edi_emploi_debut':14238,'edi_ressource_debut':14246,'edi_emploi_fin':14254,'edi_ressource_fin':14262,'parent_id':self.id,},
                                                                    {'name':'* REMBOURSEMENT DES DETTES DE FINANCEMENT (G)','edi_emploi_debut':14239,'edi_ressource_debut':14247,'edi_emploi_fin':14255,'edi_ressource_fin':14263,'parent_id':self.id,},
                                                                    {'name':'* EMPLOIS EN NON VALEURS (H)','edi_emploi_debut':14240,'edi_ressource_debut':14248,'edi_emploi_fin':14256,'edi_ressource_fin':14264,'parent_id':self.id,},
                                                                    {'name':'TOTAL II- EMPLOIS STABLES (E+F+G+H)','edi_emploi_debut':14266,'edi_ressource_debut':14267,'edi_emploi_fin':14268,'edi_ressource_fin':14269,'parent_id':self.id,},
                                                                    {'name':'III- VARIATION DU BESOIN DE FINANCEMENT GLOBAL (B.G.F)','edi_emploi_debut':14271,'edi_ressource_debut':14272,'edi_emploi_fin':14273,'edi_ressource_fin':14274,'parent_id':self.id,},
                                                                    {'name':'IV- VARIATION DE LA TRESORERIE','edi_emploi_debut':14276,'edi_ressource_debut':14277,'edi_emploi_fin':14278,'edi_ressource_fin':14279,'parent_id':self.id,},
                                                                    {'name':'TOTAL GENERAL','edi_emploi_debut':14281,'edi_ressource_debut':14282,'edi_emploi_fin':14283,'edi_ressource_fin':14284,'parent_id':self.id,},
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
    
    def bal_calulator_previous_years(self,codes,x):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                for entry in journal_entries:
                    if rec.fy_n_id:
                        for ref in rec.fy_n_id:
                            for item in entry.line_ids:
                                if x == 1:
                                    if ref.date_end.year-1 == entry.date.year:
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
                                else:
                                    if ref.date_end.year - 2 == entry.date.year:
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
    
    def bal_calulator_current_year(self,codes,n):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                for entry in journal_entries:
                    if rec.fy_n_id:
                        for ref in rec.fy_n_id:
                            for item in entry.line_ids:
                                if n == 0:
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
                                elif n==1:
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
    
    def credit_current_year(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                for entry in journal_entries:
                    if rec.fy_n_id:
                        for ref in rec.fy_n_id:
                            if ref.date_end.year == entry.date.year:
                                for item in entry.line_ids:
                                    item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                    col = rec.from_string_to_list(code,col)
                                    if rec.list_verification(col,item_code):
                                        bal += item.credit                                        
            return bal
    
    def debit_current_year(self,codes):
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
                                        bal += item.debit                                        
            return bal

    def credit_prev_year(self,codes,x):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                if rec.fy_n_id:
                    for ref in rec.fy_n_id:
                        for entry in journal_entries:
                            if x==1:
                                if ref.date_end.year - 1 == entry.date.year:
                                    for item in entry.line_ids:
                                        item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                        col = rec.from_string_to_list(code,col)
                                        if rec.list_verification(col,item_code):
                                            bal += item.credit
                            else:
                                if ref.date_end.year - 2 == entry.date.year:
                                    for item in entry.line_ids:
                                        item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                        col = rec.from_string_to_list(code,col)
                                        if rec.list_verification(col,item_code):
                                            bal += item.credit                                      
            return bal
    
    def debit_prev_year(self,codes,x):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                if rec.fy_n_id:
                    for ref in rec.fy_n_id:
                        for entry in journal_entries:
                            if x==1:
                                if ref.date_end.year - 1 == entry.date.year:
                                    for item in entry.line_ids:
                                        item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                        col = rec.from_string_to_list(code,col)
                                        if rec.list_verification(col,item_code):
                                            bal += item.debit
                            elif x==2:
                                if ref.date_end.year - 2 == entry.date.year:
                                    for item in entry.line_ids:
                                        item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                        col = rec.from_string_to_list(code,col)
                                        if rec.list_verification(col,item_code):
                                            bal += item.debit 
                            elif x==0:
                                if ref.date_end.year >= entry.date.year:
                                    for item in entry.line_ids:
                                        item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                        col = rec.from_string_to_list(code,col)
                                        if rec.list_verification(col,item_code):
                                            bal += item.debit   
                            else:
                                if ref.date_end.year > entry.date.year:
                                    for item in entry.line_ids:
                                        item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                        col = rec.from_string_to_list(code,col)
                                        if rec.list_verification(col,item_code):
                                            bal += item.debit                                   
            return bal
    
    def get_xml(self,parent):
        pass
                
    def get_lines(self):
        for rec in self:
            line_2 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Capacité d\'autofinancement')])
            line_2.write({
                'emploi_debut':0,
                'ressource_debut':abs(self.bal_calulator_current_year(['71','73','75','639','659','651','619'],1) - self.bal_calulator_current_year(['751','739','759','719','61','63','65','67'],1)),
                'emploi_fin':0,
                'ressource_fin':abs(self.bal_calulator_previous_years(['71','73','75','639','659','651','619'],1)-self.bal_calulator_previous_years(['751','739','759','719','61','63','65','67'],1)),
            })
            line_3 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Distribution de bénéfices')])
            line_3.write({
                'emploi_debut':0,
                'ressource_debut':abs(self.debit_prev_year(['4465'],0)),
                'emploi_fin':0,
                'ressource_fin':abs(self.debit_prev_year(['4465'],3)),
                })
            line_1 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','* AUTOFINANCEMENT (A)')])
            line_1.write({
               'emploi_debut':0,
                'ressource_debut':line_2.ressource_debut - line_3.ressource_debut,
                'emploi_fin':0,
                'ressource_fin':line_2.ressource_fin - line_3.ressource_fin,
            })
            
            line_5 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Cessions d\'immobilisations incorporelles')])
            line_5.write({
                'emploi_debut':0,
                'ressource_debut':abs(self.credit_current_year(['7512'])),
                'emploi_fin':0,
                'ressource_fin':abs(self.credit_prev_year(['7512'],1)),
                })
            line_6 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Cessions d\'immobilisations corporelles')])
            line_6.write({
                'emploi_debut':0,
                'ressource_debut':abs(self.credit_current_year(['7513'])),
                'emploi_fin':0,
                'ressource_fin':abs(self.credit_prev_year(['7513'],1)),
                })
            line_7 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Cessions d\'immobilisations financières')])
            line_7.write({
                'emploi_debut':0,
                'ressource_debut':abs(self.credit_current_year(['7514'])),
                'emploi_fin':0,
                'ressource_fin':abs(self.credit_prev_year(['7514'],1)),
            })
            line_8 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Récupérations sur créances immobilisées')])
            line_8.write({
                'emploi_debut':0,
                'ressource_debut':abs(self.credit_current_year(['24'])),
                'emploi_fin':0,
                'ressource_fin':abs(self.credit_prev_year(['24'],1)),
            })
            line_4 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','* CESSIONS ET REDUCTIONS D\'IMMOBILISATIONS (B)')])
            line_4.write({
                'emploi_debut':line_5.emploi_debut + line_6.emploi_debut + line_7.emploi_debut + line_8.emploi_debut,
                'ressource_debut':line_5.ressource_debut + line_6.ressource_debut + line_7.ressource_debut + line_8.ressource_debut,
                'emploi_fin':line_5.emploi_fin + line_6.emploi_fin + line_7.emploi_fin + line_8.emploi_fin,
                'ressource_fin':line_5.ressource_fin + line_6.ressource_fin + line_7.ressource_fin + line_8.ressource_fin,
                })
            
            line_10 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Augmentations de capital, apports')])
            line_10.write({
                'emploi_debut':0,
                'ressource_debut':abs(self.credit_current_year(['111','112'])),
                'emploi_fin':0,
                'ressource_fin':abs(self.credit_prev_year(['111','112'],1)),
            })
            line_11 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Subventions d\'investissement')])
            line_11.write({
                'emploi_debut':0,
                'ressource_debut':abs(self.credit_current_year(['131'])),
                'emploi_fin':0,
                'ressource_fin':abs(self.credit_prev_year(['131'],1)),
            })
            line_9 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','* AUGEMENTATION DES CAPITAUX PROPRES ET ASSIMILES (C)')])
            line_9.write({
                'emploi_debut':line_10.emploi_debut + line_11.emploi_debut,
                'ressource_debut': line_10.ressource_debut + line_11.ressource_debut,
                'emploi_fin': line_10.emploi_fin + line_11.emploi_fin,
                'ressource_fin': line_10.ressource_fin + line_11.ressource_fin,
            })
            line_12 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','* AUGMENTATION DES DETTES DE FINANCEMENT (D) (nettes des primes de remboursements)')])
            line_12.write({
                'emploi_debut':0,
                'ressource_debut':abs(self.credit_current_year(['14'])),
                'emploi_fin':0,
                'ressource_fin':abs(self.credit_prev_year(['14'],1)),
            })
            line_13 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','TOTAL I- RESSOURCES STABLES (A+B+C+D)')])
            line_13.write({
                'emploi_debut':line_1.emploi_debut + line_4.emploi_debut + line_9.emploi_debut + line_12.emploi_debut,
                'ressource_debut':line_1.ressource_debut + line_4.ressource_debut + line_9.ressource_debut + line_12.ressource_debut,
                'emploi_fin':line_1.emploi_fin + line_4.emploi_fin + line_9.emploi_fin + line_12.emploi_fin,
                'ressource_fin':line_1.ressource_fin + line_4.ressource_fin + line_9.ressource_fin + line_12.ressource_fin,
            })
            print(self.env.company.id, 'company _ id')
            table_4 = self.env['immo.financiere'].search([('fy_n_id','=',self.fy_n_id.id),('company_id','=',self.env.company.id)])
            table_4_line_1 = self.env['immo.financiere.line'].search([('name','=','IMMOBILISATIONS INCORPORELLES'),('immo_id','=',table_4.id)])
            table_4_line_2 = self.env['immo.financiere.line'].search([('name','=','IMMOBILISATIONS CORPORELLES'),('immo_id','=',table_4.id)])
            table_4_line_3 = self.env['immo.financiere.line'].search([('name','=','* Immobilisations corporelles en cours'),('immo_id','=',table_4.id)])
            table_4_prevs = self.env['immo.financiere'].search([('id','!=',False),('company_id','=',self.env.company.id)])
            if len(table_4_prevs)>0:
                for table_4_prev in table_4_prevs:
                    if table_4_prev.fy_n_id.date_end.year  == rec.fy_n_id.date_end.year - 1:
                        table_4_line_1_prev = self.env['immo.financiere.line'].search([('name','=','IMMOBILISATIONS INCORPORELLES'),('immo_id','=',table_4_prev.id)])
                        table_4_line_2_prev = self.env['immo.financiere.line'].search([('name','=','IMMOBILISATIONS CORPORELLES'),('immo_id','=',table_4_prev.id)])
                        table_4_line_3_prev = self.env['immo.financiere.line'].search([('name','=','* Immobilisations corporelles en cours'),('immo_id','=',table_4_prev.id)])
                        line_16 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Acquisitions d\'immobilisations incorporelles')])
                        line_16.write({
                            'emploi_debut':table_4_line_1.augmentation_acquisition,
                            'ressource_debut':0,
                            'emploi_fin':table_4_line_1_prev.augmentation_acquisition,
                            'ressource_fin':0,
                        })
                        line_17 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Acquisitions d\'immobilisations corporelles')])
                        line_17.write({
                            'emploi_debut':table_4_line_2.augmentation_acquisition - table_4_line_3.diminution_transaction + table_4_line_2.augmentation_production + table_4_line_2.augmentation_transaction,
                            'ressource_debut':0,
                            'emploi_fin':table_4_line_2_prev.augmentation_acquisition - table_4_line_3_prev.diminution_transaction + table_4_line_2_prev.augmentation_production + table_4_line_2_prev.augmentation_transaction,
                            'ressource_fin':0,
                        })
                    else:
                        line_16 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Acquisitions d\'immobilisations incorporelles')])
                        line_16.write({
                            'emploi_debut':table_4_line_1.augmentation_acquisition,
                            'ressource_debut':0,
                            'emploi_fin':0,
                            'ressource_fin':0,
                        })
                        line_17 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Acquisitions d\'immobilisations corporelles')])
                        line_17.write({
                            'emploi_debut':table_4_line_2.augmentation_acquisition - table_4_line_3.diminution_transaction + table_4_line_2.augmentation_production + table_4_line_2.augmentation_transaction,
                            'ressource_debut':0,
                            'emploi_fin':0,
                            'ressource_fin':0,
                        })
            else:
                line_16 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Acquisitions d\'immobilisations incorporelles')])
                line_16.write({
                    'emploi_debut':0,
                    'ressource_debut':0,
                    'emploi_fin':0,
                    'ressource_fin':0,
                })
                line_17 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Acquisitions d\'immobilisations corporelles')])
                line_17.write({
                    'emploi_debut':0,
                    'ressource_debut':0,
                    'emploi_fin':0,
                    'ressource_fin':0,
                })
            line_18 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Acquisitions d\'immobilisations financières')])
            line_18.write({
                'emploi_debut':abs(self.debit_current_year(['25'])),
                'ressource_debut':0,
                'emploi_fin':abs(self.debit_prev_year(['25'],1)),
                'ressource_fin':0,
            })
            line_19 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','- Augmentation des créances immobilisées')])
            line_19.write({
                'emploi_debut':abs(self.debit_current_year(['24'])),
                'ressource_debut':0,
                'emploi_fin':abs(self.debit_prev_year(['24'],1)),
                'ressource_fin':0,
            })
            line_15 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','* ACQUISITIONS ET AUGEMENTATIONS D\'IMMOBILISATIONS (E)')])
            line_15.write({
                'emploi_debut': line_16.emploi_debut + line_17.emploi_debut + line_18.emploi_debut + line_19.emploi_debut,
                'ressource_debut':line_16.ressource_debut + line_17.ressource_debut + line_18.ressource_debut + line_19.ressource_debut,
                'emploi_fin':line_16.emploi_fin + line_17.emploi_fin + line_18.emploi_fin + line_19.emploi_fin,
                'ressource_fin':line_16.ressource_fin + line_17.ressource_fin + line_18.ressource_fin + line_19.ressource_fin,
            })
            line_20 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','* REMBOURSEMENT DES CAPITAUX PROPRES (F)')])
            line_20.write({
                'emploi_debut':abs(self.debit_current_year(['111','131'])),
                'ressource_debut':0,
                'emploi_fin':abs(self.debit_prev_year(['111','131'],1)),
                'ressource_fin':0,
            })
            line_21 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','* REMBOURSEMENT DES DETTES DE FINANCEMENT (G)')])
            line_21.write({
                'emploi_debut':abs(self.debit_current_year(['14'])),
                'ressource_debut':0,
                'emploi_fin':abs(self.debit_prev_year(['14'],1)),
                'ressource_fin':0,
            })
            line_22 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','* EMPLOIS EN NON VALEURS (H)')])
            line_22.write({
                'emploi_debut':abs(self.debit_current_year(['21'])),
                'ressource_debut':0,
                'emploi_fin':abs(self.debit_prev_year(['21'],1)),
                'ressource_fin':0,
            })
            line_23 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','TOTAL II- EMPLOIS STABLES (E+F+G+H)')])
            line_23.write({
                'emploi_debut':line_15.emploi_debut + line_20.emploi_debut + line_21.emploi_debut + line_22.emploi_debut,
                'ressource_debut':line_15.ressource_debut + line_20.ressource_debut + line_21.ressource_debut + line_22.ressource_debut,
                'emploi_fin':line_15.emploi_fin + line_20.emploi_fin + line_21.emploi_fin + line_22.emploi_fin,
                'ressource_fin':line_15.ressource_fin + line_20.ressource_fin + line_21.ressource_fin + line_22.ressource_fin,
            })
            financement_year = self.env['finance.first'].search([('fy_n_id','=',rec.fy_n_id.id),('company_id','=',self.env.company.id)])
            financement_year_line_1 = self.env['finance.first.line'].search([('name','=','6- BESOIN DE FINANCEMENT GLOBAL (4 - 5) (B)'),('parent_id','=',financement_year.id)])
            financement_year_line_2 = self.env['finance.first.line'].search([('name','=','7- TRESORERIE NETTE (ACTIF - PASSIF) = A - B'),('parent_id','=',financement_year.id)])
            financement_prevs = self.env['finance.first'].search([('id','!=',False),('company_id','=',self.env.company.id)])
            if len(financement_prevs)>0:
                for financement_prev in financement_prevs:
                    if financement_prev.fy_n_id.date_end.year  == rec.fy_n_id.date_end.year - 1:
                        financement_line_1_prev =self.env['finance.first.line'].search([('name','=','6- BESOIN DE FINANCEMENT GLOBAL (4 - 5) (B)'),('parent_id','=',financement_prev.id)])
                        financement_line_2_prev = self.env['finance.first.line'].search([('name','=','7- TRESORERIE NETTE (ACTIF - PASSIF) = A - B'),('parent_id','=',financement_prev.id)])
                        line_24 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','III- VARIATION DU BESOIN DE FINANCEMENT GLOBAL (B.G.F)')])
                        line_24.write({
                            'emploi_debut':financement_year_line_1.p_debit_fin,
                            'ressource_debut':financement_year_line_1.n_debit_fin,
                            'emploi_fin':financement_line_1_prev.p_debit_fin,
                            'ressource_fin':financement_line_1_prev.n_debit_fin,
                        })
                        line_25 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','IV- VARIATION DE LA TRESORERIE')])
                        line_25.write({
                            'emploi_debut':financement_year_line_2.p_debit_fin,
                            'ressource_debut':financement_year_line_2.n_debit_fin,
                            'emploi_fin':financement_line_2_prev.p_debit_fin,
                            'ressource_fin':financement_line_2_prev.n_debit_fin
                        })
                    else:
                        line_24 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','III- VARIATION DU BESOIN DE FINANCEMENT GLOBAL (B.G.F)')])
                        line_24.write({
                            'emploi_debut':financement_year_line_1.p_debit_fin,
                            'ressource_debut':financement_year_line_1.n_debit_fin,
                            'emploi_fin':0,
                            'ressource_fin':0,
                        })
                        line_25 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','IV- VARIATION DE LA TRESORERIE')])
                        line_25.write({
                            'emploi_debut':financement_year_line_2.p_debit_fin,
                            'ressource_debut':financement_year_line_2.n_debit_fin,
                            'emploi_fin':0,
                            'ressource_fin':0,
                        })
            else:
                line_24 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','III- VARIATION DU BESOIN DE FINANCEMENT GLOBAL (B.G.F)')])
                line_24.write({
                    'emploi_debut':0,
                    'ressource_debut':0,
                    'emploi_fin':0,
                    'ressource_fin':0,
                })
                line_25 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','IV- VARIATION DE LA TRESORERIE')])
                line_25.write({
                    'emploi_debut':0,
                    'ressource_debut':0,
                    'emploi_fin':0,
                    'ressource_fin':0,
                })
            line_26 = self.env['finance.second.line'].search([('parent_id','=',rec.id),('name','=','TOTAL GENERAL')])
            line_26.write({
                'emploi_debut':line_23.emploi_debut + line_24.emploi_debut + line_25.emploi_debut ,
                'ressource_debut':line_24.ressource_debut + line_13.ressource_debut + line_25.ressource_debut,
                'emploi_fin':line_25.emploi_fin + line_23.emploi_fin+ line_24.emploi_fin,
                'ressource_fin':line_25.ressource_fin + line_13.ressource_fin + line_24.ressource_fin,
            })

    def get_xml(self,parent):
        for rec in self:
            if rec.line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(203) # read documentation XML
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                financement_first = self.env['finance.first'].search([('fy_n_id','=',rec.fy_n_id.id),('company_id','=',self.env.company.id)])
                if financement_first:
                    for line in financement_first.line_ids:
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.edi_montant_debut)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_debut)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.edi_montant_fin)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_fin)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.edi_p_debit_fin)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.p_debit_fin)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.edi_n_debit_fin)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.n_debit_fin)
                for line in rec.line_ids:
                    if line.name != 'II- EMPLOIS ET RESSOURCES- II- EMPLOIS STABLES DE L\'EXERCICE (FLUX)':
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.edi_emploi_debut)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.emploi_debut)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.edi_ressource_debut)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.ressource_debut)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.edi_emploi_fin)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.emploi_fin)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.edi_ressource_fin)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.ressource_fin)
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
            else:
                pass
class FinanceSecondLine(models.Model):
    _name = 'finance.second.line'  
    _description = 'LIGNES TABLEAU DE FINANCE'

    name = fields.Char(string=u"II- EMPLOIS ET RESSOURCES- I- RESSOURCES STABLES DE L'EXERCICE (FLUX)",required=True,readonly=True)
    emploi_debut = fields.Float(string=u"EMPLOI EXERCICE",  required=False,readonly=True )
    ressource_debut = fields.Float(string=u"RESSOURCE EXERCICE",  required=False,readonly=True )
    emploi_fin = fields.Float(string=u"EMPLOI EXERCICE PRECEDENT",  required=False, readonly=True )
    ressource_fin = fields.Float(string=u"RESSOURCE EXERCICE PRECEDENT",  required=False, readonly=True )
    
    
    # Code Edi
    edi_emploi_debut = fields.Integer(string=u"EMPLOI EXERCICE",  required=False,readonly=True )
    edi_ressource_debut = fields.Integer(string=u"RESSOURCE EXERCICE",  required=False,readonly=True )
    edi_emploi_fin = fields.Integer(string=u"EMPLOI EXERCICE PRECEDENT",  required=False, readonly=True )
    edi_ressource_fin = fields.Integer(string=u"RESSOURCE EXERCICE PRECEDENT",  required=False, readonly=True )
    
    # Relational Fields
    parent_id = fields.Many2one(comodel_name="finance.second", string="finance", required=False, readonly=True  )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('finance.second.line'))