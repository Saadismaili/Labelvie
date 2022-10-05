# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)


class Resultats(models.Model):
    _name = 'resultats'
    _description = 'RESULTATS ET AUTRES ELEMENTS CARACTERISTIQUES DE L\'ENTREPRISE AU COURS DES TROIS DERNIERS EXERCICES'

    name = fields.Char(string=u"Nom",default="RESULTATS ET AUTRES ELEMENTS CARACTERISTIQUES DE L'ENTREPRISE AU COURS DES TROIS DERNIERS EXERCICES",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    line_ids = fields.One2many(comodel_name="resultats.line", inverse_name="parent_id", string="Lignes", required=False, copy=True )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('finance.first'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    @api.model
    def create(self, values):
        return super(Resultats,self).create({
            'fy_n_id':self.fy_n_id.id,
            'line_ids' : self.env['resultats.line'].create([{'name':'SITUATION NETTE DE L\'ENTREPRISE','parent_id':self.id,},
                                                                        {'name':'1. Capitaux propres plus capitaux propres assimilÈs moins immobilisation en','parent_id':self.id,},
                                                                        {'name':'OPERATIONS ET RESULTATS DE L\'EXERCICE','parent_id':self.id,},
                                                                        {'name':'1. Chiffre d\'affaires hors taxes','parent_id':self.id,},
                                                                        {'name':'2. RÈsultat avant impÙts','parent_id':self.id,},
                                                                        {'name':'3. ImpÙts sur les rÈsultats','parent_id':self.id,},
                                                                        {'name':'4. BÈnÈfices distribuÈs','parent_id':self.id,},
                                                                        {'name':'5. RÈsultats non distribuÈs ( mis en rÈserves ou en instance d\'affectation','parent_id':self.id,},
                                                                        {'name':'RESULTAT PAR TITRE ( Pour les sociÈtÈs par actions et S.A.R.L.)','parent_id':self.id,},
                                                                        {'name':'1. RÈsultat net par action ou part sociale','parent_id':self.id,},
                                                                        {'name':'2. BÈnÈfices distribuÈs par action ou part sociale','parent_id':self.id,},
                                                                        {'name':'PERSONNEL','parent_id':self.id,},
                                                                        {'name':'1. Montant des salaires bruts de l\'exercice','parent_id':self.id,},
                                                                        {'name':'2. Effectif moyen des salariÈs employÈs pendant l\'exercice','parent_id':self.id,},
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

    def bal_calulator_second_previous_years(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                for entry in journal_entries:
                    if rec.fy_n_id:
                        for ref in rec.fy_n_id:
                            for item in entry.line_ids:
                                if ref.date_end.year - 1 > entry.date.year:
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
                            if ref.date_end.year >= entry.date.year:
                                for item in entry.line_ids:
                                    item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                    col = rec.from_string_to_list(code,col)
                                    if rec.list_verification(col,item_code):
                                        bal += item.credit                                        
            return bal
    
    def credit_prev_year(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                for entry in journal_entries:
                    if rec.fy_n_id:
                        for ref in rec.fy_n_id:
                            if ref.date_end.year > entry.date.year:
                                for item in entry.line_ids:
                                    item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                    col = rec.from_string_to_list(code,col)
                                    if rec.list_verification(col,item_code):
                                        bal += item.credit                                        
            return bal
        
    def credit_second_prev_year(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                for entry in journal_entries:
                    if rec.fy_n_id:
                        for ref in rec.fy_n_id:
                            if ref.date_end.year - 1 > entry.date.year:
                                for item in entry.line_ids:
                                    item_code = rec.from_string_to_list(item.account_id.code,item_code)
                                    col = rec.from_string_to_list(code,col)
                                    if rec.list_verification(col,item_code):
                                        bal += item.credit                                        
            return bal
    
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
    
    def bal_calulator_net_second_prev(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                for entry in journal_entries:
                    if rec.fy_n_id:
                        for ref in rec.fy_n_id:
                            for item in entry.line_ids:
                                if ref.date_end.year -2 == entry.date.year:
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
        for res in self:
            line_1 = self.env['resultats.line'].search([('name','=','1. Capitaux propres plus capitaux propres assimilÈs moins immobilisation en'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_1.write({
                'amount_n_2':res.bal_calulator_second_previous_years(['13']),
                'amount_n_1':res.bal_calulator_previous_years(['13']),
                'amount_n':res.bal_calulator_current_year(['13']),
            })
            line_2 = self.env['resultats.line'].search([('name','=','SITUATION NETTE DE L\'ENTREPRISE'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_2.write({
                'amount_n_2':line_1.amount_n_2,
                'amount_n_1':line_1.amount_n_1,
                'amount_n':line_1.amount_n,
            })
            line_3 = self.env['resultats.line'].search([('name','=','1. Chiffre d\'affaires hors taxes'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_3.write({
                'amount_n_2':res.bal_calulator_net_second_prev(['712','711']),
                'amount_n_1':res.bal_calulator_net_prev(['712','711']),
                'amount_n':res.bal_calulator_net_year(['712','711']),
            })
            line_4 = self.env['resultats.line'].search([('name','=','2. RÈsultat avant impÙts'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_4.write({
                'amount_n_2':0,
                'amount_n_1':0,
                'amount_n':0,
            })
            line_5 = self.env['resultats.line'].search([('name','=','3. ImpÙts sur les rÈsultats'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_5.write({
                'amount_n_2':res.bal_calulator_net_second_prev(['67']),
                'amount_n_1':res.bal_calulator_net_prev(['67']),
                'amount_n':res.bal_calulator_net_year(['67']),
            })
            line_6= self.env['resultats.line'].search([('name','=','4. BÈnÈfices distribuÈs'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_6.write({
                'amount_n_2':res.credit_current_year(['4465']),
                'amount_n_1':res.credit_current_year(['4465']),
                'amount_n':res.credit_current_year(['4465']),
            })
            line_7 = self.env['resultats.line'].search([('name','=','5. RÈsultats non distribuÈs ( mis en rÈserves ou en instance d\'affectation'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_7.write({
                'amount_n_2':0,
                'amount_n_1':0,
                'amount_n':0,
            })
            
            line_8 = self.env['resultats.line'].search([('name','=','OPERATIONS ET RESULTATS DE L\'EXERCICE'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_8.write({
                'amount_n_2':line_3.amount_n_2 + line_4.amount_n_2 + line_5.amount_n_2 + line_6.amount_n_2 + line_7.amount_n_2 ,
                'amount_n_1':line_3.amount_n_1 + line_4.amount_n_1 + line_5.amount_n_1 + line_6.amount_n_1 + line_7.amount_n_1 ,
                'amount_n':line_3.amount_n + line_4.amount_n + line_5.amount_n + line_6.amount_n + line_7.amount_n ,
            })
            line_9 = self.env['resultats.line'].search([('name','=','1. RÈsultat net par action ou part sociale'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_9.write({
                'amount_n_2':0,
                'amount_n_1':0,
                'amount_n':0,
            })
            line_10 = self.env['resultats.line'].search([('name','=','2. BÈnÈfices distribuÈs par action ou part sociale'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_10.write({
                'amount_n_2':res.credit_current_year(['4465']),
                'amount_n_1':res.credit_current_year(['4465']),
                'amount_n':res.credit_current_year(['4465']),
            })
            line_11 = self.env['resultats.line'].search([('name','=','RESULTAT PAR TITRE ( Pour les sociÈtÈs par actions et S.A.R.L.)'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_11.write({
                 'amount_n_2':line_9.amount_n_2 + line_10.amount_n_2,
                'amount_n_1':line_9.amount_n_1 + line_10.amount_n_1,
                'amount_n':line_9.amount_n + line_10.amount_n,
            })
            line_12 = self.env['resultats.line'].search([('name','=','1. Montant des salaires bruts de l\'exercice'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_12.write({
                'amount_n_2':0,
                'amount_n_1':0,
                'amount_n':0,
            })
            line_13 = self.env['resultats.line'].search([('name','=','2. Effectif moyen des salariÈs employÈs pendant l\'exercice'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_13.write({
                'amount_n_2':0,
                'amount_n_1':0,
                'amount_n':0,
            })
            line_14 = self.env['resultats.line'].search([('name','=','PERSONNEL'),('parent_id','=',res.id),('company_id','=',self.env.company.id)])
            line_14.write({
                'amount_n_2':line_12.amount_n_2 + line_13.amount_n_2,
                'amount_n_1':line_12.amount_n_1 + line_13.amount_n_1,
                'amount_n':line_12.amount_n + line_13.amount_n,
            })

class ResultatsLine(models.Model):
    _name = 'resultats.line' 
    _description = 'LIGNES TABLEAU DE FINANCE'

    name = fields.Char(string=u"NATURES DES INDICATIONS",required=True,readonly=True)
    amount_n_2 = fields.Float(string=u"EXCERCICE N-2",  required=False,readonly=True )
    amount_n_1 = fields.Float(string=u"EXCERCICE N-1",  required=False, readonly=True )
    amount_n = fields.Float(string=u"EXCERCICE N",  required=False, readonly=True )
    parent_id = fields.Many2one(comodel_name="resultats", string="Resultats", required=False, readonly=True  )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('finance.first.line'))