
from odoo import models, fields, api, _ 

from lxml import etree
import base64
import zipfile

import os
directory = os.path.dirname(__file__)  

class ControlTable(models.Model):
    
    _name = 'control.table'
    
    name = fields.Char(string='Nom',default = 'Controle des etats de syntheses')
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    line_ids = fields.One2many(comodel_name="control.table.line", inverse_name="parent_id", string="Lignes", required=False, copy=True )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('control.table'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    
    @api.model
    def create(self, values):
        return super(ControlTable,self).create({
            'fy_n_id':self.fy_n_id.id,
            'line_ids' : self.env['control.table.line'].create([{'name':'Total Brut Bilan & Solde Final Balance','parent_id':self.id,},
                                                                        {'name':'Total Net Bilan & Solde Final Balance','parent_id':self.id,},
                                                                        {'name':'Equilibre N: Actif & Passif','parent_id':self.id,},
                                                                        {'name':'Equilibre N-1: Actif & Passif','parent_id':self.id,},
                                                                        {'name':'Resultats : Passif & CPC','parent_id':self.id,},
                                                                        {'name':'Equilibre table de finnancement N','parent_id':self.id,},
                                                                        {'name':'Equilibre table de finnancement N-1','parent_id':self.id,},
                                                                        {'name':'Resultats Net : Passif & T3 passage','parent_id':self.id,},
                                                                        {'name':'IMMO en non valeur : Actif & T4 Des IMMO','parent_id':self.id,},
                                                                        {'name':'Amortissements IMM en non valeur & T8 des Amortissements','parent_id':self.id,},
                                                                        {'name':'IMMO incor & T4 Des IMMO','parent_id':self.id,},
                                                                        {'name':'AMORT IMMO incor: Actif & T8 Des Amortissements','parent_id':self.id,},
                                                                        {'name':'IMMO CORPOR & T4 des IMMO','parent_id':self.id,},
                                                                        {'name':'AMORT IMMO CORPOR: Actif & T8 Des Amortissements','parent_id':self.id,},
                                                                        {'name':'PROV DUR PR R et CH : passif & T9 tab des PROV','parent_id':self.id,},
                                                                        {'name':'Stock(Brut) : Actif & T20 etat stocks','parent_id':self.id,},
                                                                        {'name':'Stock(Net) : Actif & T20 etat stocks','parent_id':self.id,},
                                                                        {'name':'MT Prov STK Actif & T20 etat stocks','parent_id':self.id,},
                                                                        {'name':'Variat STK N-(N-1): Actif & T20 etat stocks','parent_id':self.id,},
                                                                        {'name':'Variat STK MSE S N-(N-1): Actif & T6 Detail CPC','parent_id':self.id,},
                                                                        {'name':'Variat STK MSE S: Detail CPC & T20 etat stocks','parent_id':self.id,},
                                                                        # ###############################################################
                                                                        {'name':'DOT D\'EXPL : CPC T2 & TAB AMORT T8+TAB PROV T9','parent_id':self.id,},
                                                                        {'name':'LOCATION : DETAIL CPC T6 & T19 LOC ET BAUX','parent_id':self.id,},
                                                                        {'name':'VENTES DE MARCH(N) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'VENTES DE MARCH(N-1) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'VENT B & SERV PRD(N) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'VENT B & SERV PRD(N-1) : CPC T2 & T6 DETAIL','parent_id':self.id,},
                                                                        {'name':'VAR DE STK PRD(N) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'VAR DE STK PRD(N-1) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'AUTRE PRD D\'EXPL(N) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'AUTRE PRD D\'EXPL(N-1) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'REPR D\'EXPL : TRANSF DE CH(N) : CPC T2 & T6 DETAIL','parent_id':self.id,},
                                                                        {'name':'REPR D\'EXPL : TRANSF DE CH(N-1) : CPC T2 & T6 DETAIL','parent_id':self.id,},
                                                                        {'name':'ACH REV DE MSES(N) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'ACH REV DE MSES(N-1) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'ACH CONS DE MAT&FOUR(N) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'AUTRE CH EXT(N) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'AUTRE CH EXT(N-1) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'CH DE PERSONNEL(N) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'CH DE PERSONNEL(N-1) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'AUT CH D\'EXP(N) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'AUT CH D\'EXP(N-1) : CPC T2 & T6 DETAIL CPC','parent_id':self.id,},
                                                                        {'name':'FC : ACTIF & T4 TAB DES IMM','parent_id':self.id,},
                                                                        {'name':'AUT IMM INCOR : ACTIF & T4 TAB DES IMMO','parent_id':self.id,},
                                                                        {'name':'TERRAIN : ACTIF & T4 TAB DES IMMO','parent_id':self.id,},
                                                                        {'name':'CONSTRUCTION : ACTIF & T4 TAB DES IMMO','parent_id':self.id,},
                                                                        {'name':'INT : ACTIF & TAB DES IMMO','parent_id':self.id,},
                                                                        {'name':'MAT TRANSPORT : ACTIF & T4 TAB DES IMMO','parent_id':self.id,},
                                                                        {'name':'IMMB ET AMENAG : ACTIF & T4 TAB DES IMMO','parent_id':self.id,},
                                                                        {'name':'REDEV CREDIT-Bail : T7 TAB DES BIENS CRD-BAIL &  T6 DETAIL CPC','parent_id':self.id,},
                                                                        
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
            line_1 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Total Brut Bilan & Solde Final Balance')])
            line_1.write({
                'first_amount':  self.bal_calulator_current_year(['21','22','23','24','25','27','31','34','51'])  ,
                'second_amount':  self.bal_calulator_current_year(['21','22','23','24','25','27','31','34','51'])  ,
                'diff_amount':  0 ,
            })
            line_2 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Total Net Bilan & Solde Final Balance')])
            line_2.write({
                'first_amount':  self.bal_calulator_current_year(['21','22','23','24','25','27','31','34','51']) - self.bal_calulator_current_year(['281','282','283','294','295','391','394','59']) ,
                'second_amount':  self.bal_calulator_current_year(['21','22','23','24','25','27','31','34','51']) - self.bal_calulator_current_year(['281','282','283','294','295','391','394','59']) ,
                'diff_amount':  0 ,
            })
            line_3 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Equilibre N: Actif & Passif')])
            line_3.write({
                'first_amount':  self.bal_calulator_current_year(['21','22','23','24','25','27','31','34','51']) - self.bal_calulator_current_year(['281','282','283','294','295','391','394','59']) ,
                'second_amount':  self.bal_calulator_current_year(['21','22','23','24','25','27','31','34','51']) - self.bal_calulator_current_year(['281','282','283','294','295','391','394','59']) ,
                'diff_amount':  0 ,
            })
            line_4 =self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Equilibre N-1: Actif & Passif')])
            line_4.write({
                'first_amount':  self.bal_calulator_previous_years(['21','22','23','24','25','27','31','34','51']) - self.bal_calulator_previous_years(['281','282','283','294','295','391','394','59']) ,
                'second_amount':  self.bal_calulator_previous_years(['21','22','23','24','25','27','31','34','51']) - self.bal_calulator_previous_years(['281','282','283','294','295','391','394','59']) ,
                'diff_amount':  0 ,
            })
            
            line_6 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Resultats : Passif & CPC')])
            line_6.write({
                'first_amount':   self.bal_calulator_net_year(['71','73','75']) - self.bal_calulator_net_year(['61','63','65','67']) ,
                'second_amount':   self.bal_calulator_net_year(['71','73','75']) - self.bal_calulator_net_year(['61','63','65','67']) ,
                'diff_amount':  0 ,
            })
            line_7 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Equilibre table de finnancement N')])
            line_7.write({
                'first_amount':  self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]).emploi_debut if self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]) else 0,
                'second_amount':  self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]).ressource_debut if self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]) else 0,
                'diff_amount':  self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]).emploi_debut - self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]).ressource_debut if self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_8 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Equilibre table de finnancement N-1')])
            line_8.write({
                'first_amount':  self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]).emploi_fin if self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]) else 0,
                'second_amount':  self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]).ressource_fin if self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]) else 0,
                'diff_amount':  self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]).emploi_fin - self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]).ressource_fin if  self.env['finance.second.line'].search([('parent_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL GENERAL'),('company_id','=',self.env.company.id)]) else 0,
            })
            line_9 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Resultats Net : Passif & T3 passage')])
            line_9.write({
                'first_amount':   self.bal_calulator_net_year(['71','73','75']) - self.bal_calulator_net_year(['61','63','65','67']) ,
                'second_amount':   self.bal_calulator_net_year(['71','73','75']) - self.bal_calulator_net_year(['61','63','65','67']) ,
                'diff_amount':  0 ,
            })
            line_10 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','IMMO en non valeur : Actif & T4 Des IMMO')])
            line_10.write({
                'first_amount': self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATION EN NON-VALEURS'),('company_id','=',self.env.company.id)]).montant_end if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATION EN NON-VALEURS'),('company_id','=',self.env.company.id)]) else 0 ,
                'second_amount':   self.bal_calulator_current_year(['21'])  ,
                'diff_amount':  self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATION EN NON-VALEURS'),('company_id','=',self.env.company.id)]).montant_end - self.bal_calulator_current_year(['21']) if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATION EN NON-VALEURS'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_11 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Amortissements IMM en non valeur & T8 des Amortissements')])
            line_11.write({
                'first_amount':  self.env['immo.amortissements.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATION EN NON-VALEURS'),('company_id','=',self.env.company.id)]).cumule_amortissement if self.env['immo.amortissements.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATION EN NON-VALEURS'),('company_id','=',self.env.company.id)]) else 0,
                'second_amount': self.bal_calulator_current_year(['281']) ,
                'diff_amount':  self.env['immo.amortissements.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATION EN NON-VALEURS'),('company_id','=',self.env.company.id)]).cumule_amortissement - self.bal_calulator_current_year(['281']) if self.env['immo.amortissements.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATION EN NON-VALEURS'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_12 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','IMMO incor & T4 Des IMMO')])
            line_12.write({
                'first_amount':  self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS INCORPORELLES'),('company_id','=',self.env.company.id)]).montant_end if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS INCORPORELLES'),('company_id','=',self.env.company.id)]) else 0 ,
                'second_amount': self.bal_calulator_current_year(['22'])  ,
                'diff_amount':  self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS INCORPORELLES'),('company_id','=',self.env.company.id)]).montant_end - self.bal_calulator_current_year(['22']) if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS INCORPORELLES'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_23 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','AMORT IMMO incor: Actif & T8 Des Amortissements')])
            line_23.write({
                'first_amount':  self.env['immo.amortissements.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS INCORPORELLES'),('company_id','=',self.env.company.id)]).cumule_amortissement if self.env['immo.amortissements.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS INCORPORELLES'),('company_id','=',self.env.company.id)]) else 0,
                'second_amount': self.bal_calulator_current_year(['282']),
                'diff_amount':  self.env['immo.amortissements.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS INCORPORELLES'),('company_id','=',self.env.company.id)]).cumule_amortissement - self.bal_calulator_current_year(['282']) if self.env['immo.amortissements.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS INCORPORELLES'),('company_id','=',self.env.company.id)]) else 0,
            })
            line_13 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','IMMO CORPOR & T4 des IMMO')])
            line_13.write({
                'first_amount': self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS CORPORELLES'),('company_id','=',self.env.company.id)]).montant_end if  self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS CORPORELLES'),('company_id','=',self.env.company.id)]) else 0,
                'second_amount':  self.bal_calulator_current_year(['23']) ,
                'diff_amount':   self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS CORPORELLES'),('company_id','=',self.env.company.id)]).montant_end - self.bal_calulator_current_year(['23']) if  self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS CORPORELLES'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_14 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','AMORT IMMO CORPOR: Actif & T8 Des Amortissements')])
            line_14.write({
                'first_amount':  self.env['immo.amortissements.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS CORPORELLES'),('company_id','=',self.env.company.id)]).cumule_amortissement if self.env['immo.amortissements.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS CORPORELLES'),('company_id','=',self.env.company.id)]) else 0,
                'second_amount':  self.bal_calulator_current_year(['283']),
                'diff_amount':  self.env['immo.amortissements.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS CORPORELLES'),('company_id','=',self.env.company.id)]).cumule_amortissement - self.bal_calulator_current_year(['283']) if self.env['immo.amortissements.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','IMMOBILISATIONS CORPORELLES'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_15 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Stock(Brut) : Actif & T20 etat stocks')])
            line_15.write({
                'first_amount':  self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL  GENERAL'),('company_id','=',self.env.company.id)]).montant_brut_stock_final if self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL  GENERAL'),('company_id','=',self.env.company.id)]) else 0,
                'second_amount':  self.bal_calulator_current_year(['31']),
                'diff_amount':  self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL  GENERAL'),('company_id','=',self.env.company.id)]).montant_brut_stock_final - self.bal_calulator_current_year(['31']) if self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL  GENERAL'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_16 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Stock(Net) : Actif & T20 etat stocks')])
            line_16.write({
                'first_amount':  self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL  GENERAL'),('company_id','=',self.env.company.id)]).montant_net_stock_final if self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL  GENERAL'),('company_id','=',self.env.company.id)]) else 0,
                'second_amount':  self.bal_calulator_current_year(['31']) - self.bal_calulator_current_year(['391']),
                'diff_amount':  self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL  GENERAL'),('company_id','=',self.env.company.id)]).montant_net_stock_final - self.bal_calulator_current_year(['31']) + self.bal_calulator_current_year(['391']) if self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL  GENERAL'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            
            line_19 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Variat STK N-(N-1): Actif & T20 etat stocks')])
            line_19.write({
                'first_amount':  self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL  GENERAL'),('company_id','=',self.env.company.id)]).montant_net_stock_final if self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL  GENERAL'),('company_id','=',self.env.company.id)]) else 0,
                'second_amount':  self.bal_calulator_current_year(['31']) - self.bal_calulator_current_year(['391']),
                'diff_amount':   self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL  GENERAL'),('company_id','=',self.env.company.id)]).montant_net_stock_final - self.bal_calulator_current_year(['31']) + self.bal_calulator_current_year(['391']) if self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','TOTAL  GENERAL'),('company_id','=',self.env.company.id)]) else 0,
            })
            line_17 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','MT Prov STK Actif & T20 etat stocks')])
            line_17.write({
                'first_amount':  self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','I.STOCKS APPROVISIONNEMENT'),('company_id','=',self.env.company.id)]).montant_net_stock_final if self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','I.STOCKS APPROVISIONNEMENT'),('company_id','=',self.env.company.id)]) else 0,
                'second_amount':  self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','I.STOCKS APPROVISIONNEMENT'),('company_id','=',self.env.company.id)]).montant_net_stock_final if self.env['detail.stock.line'].search([('detail_stock_id.fy_n_id','=',rec.fy_n_id.id),('name','=','I.STOCKS APPROVISIONNEMENT'),('company_id','=',self.env.company.id)]) else 0,
                'diff_amount':  0  ,
            })
            line_20 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Variat STK MSE S N-(N-1): Actif & T6 Detail CPC')])
            line_20.write({
                'first_amount':  self.bal_calulator_net_prev(['61241']) ,#61241
                'second_amount':  self.bal_calulator_net_prev(['61241']) ,
                'diff_amount':  0 ,
            })
            line_21 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','Variat STK MSE S: Detail CPC & T20 etat stocks')])
            line_21.write({
                'first_amount': self.bal_calulator_net_year(['61241']) ,#61241
                'second_amount':  self.bal_calulator_net_year(['61241']) ,
                'diff_amount':  0 ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','PROV DUR PR R et CH : passif & T9 tab des PROV')])
            line_22.write({
                'first_amount':self.env['provisions.line'].search([('provisions_id.fy_n_id','=',rec.fy_n_id.id),('name','=','3. Provisions durables pour risques et charges'),('company_id','=',self.env.company.id)]).montant_fin if self.env['provisions.line'].search([('provisions_id.fy_n_id','=',rec.fy_n_id.id),('name','=','3. Provisions durables pour risques et charges'),('company_id','=',self.env.company.id)]) else 0 ,
                'second_amount':   self.bal_calulator_current_year(['151','155']),
                'diff_amount': self.env['provisions.line'].search([('provisions_id.fy_n_id','=',rec.fy_n_id.id),('name','=','3. Provisions durables pour risques et charges'),('company_id','=',self.env.company.id)]).montant_fin - self.bal_calulator_current_year(['151','155']) if self.env['provisions.line'].search([('provisions_id.fy_n_id','=',rec.fy_n_id.id),('name','=','3. Provisions durables pour risques et charges'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','DOT D\'EXPL : CPC T2 & TAB AMORT T8+TAB PROV T9')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_year(['619']) ,
                'second_amount':  self.bal_calulator_net_year(['619'])  ,
                'diff_amount':  0 ,
            })
            location = self.env['locations.baux'].search([('fy_n_id','=',rec.fy_n_id.id),('company_id','=',self.env.company.id)])
            amount = 0
            if location:
                for line in location.locations_baux_line_ids:
                    amount += line.montant_loyer
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','LOCATION : DETAIL CPC T6 & T19 LOC ET BAUX')])
            line_22.write({
                'first_amount':  amount ,
                'second_amount': self.bal_calulator_net_year(['6131'])  ,
                'diff_amount':  self.bal_calulator_net_year(['6131'])  - amount ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','VENTES DE MARCH(N) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_year(['7113','7111','7118','7119']) ,
                'second_amount':  self.bal_calulator_net_year(['711']),
                'diff_amount':  self.bal_calulator_net_year(['711'])  - self.bal_calulator_net_year(['7113','7111','7118','7119']) ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','VENTES DE MARCH(N-1) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_prev(['7113','7111','7118','7119']) ,
                'second_amount':  self.bal_calulator_net_prev(['711']) ,
                'diff_amount':  self.bal_calulator_net_prev(['711']) - self.bal_calulator_net_prev(['7113','7111','7118','7119']) ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','VENT B & SERV PRD(N) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_year(['7121','7122',"7124",'7125','7126','7127','7128','7129']) ,
                'second_amount':  self.bal_calulator_net_year(['712'])  ,
                'diff_amount':  self.bal_calulator_net_year(['712'])  - self.bal_calulator_net_year(['7121','7122',"7124",'7125','7126','7127','7128','7129']) ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','VENT B & SERV PRD(N-1) : CPC T2 & T6 DETAIL')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_prev(['7121','7122',"7124",'7125','7126','7127','7128','7129']) ,
                'second_amount':  self.bal_calulator_net_prev(['712']),
                'diff_amount':  self.bal_calulator_net_prev(['712'])   - self.bal_calulator_net_prev(['7121','7122',"7124",'7125','7126','7127','7128','7129']) ,
            })
            
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','VAR DE STK PRD(N) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_year(['7132','7134',"7131"]) ,
                'second_amount':  self.bal_calulator_net_year(['713'])  ,
                'diff_amount':  self.bal_calulator_net_year(['713'])  - self.bal_calulator_net_year(['7132','7134',"7131"]) ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','VAR DE STK PRD(N-1) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_prev(['7132','7134',"7131"]) ,
                'second_amount':  self.bal_calulator_net_prev(['713']),
                'diff_amount':  self.bal_calulator_net_prev(['713'])   - self.bal_calulator_net_prev(['7132','7134',"7131"]) ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','AUTRE PRD D\'EXPL(N) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
               'first_amount':  self.bal_calulator_net_year(['7181','7182',"7185",'7186','7188']) ,
                'second_amount':  self.bal_calulator_net_year(['718'])  ,
                'diff_amount':  self.bal_calulator_net_year(['718'])  - self.bal_calulator_net_year(['7181','7182',"7185",'7186','7188']) ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','AUTRE PRD D\'EXPL(N-1) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_prev(['7181','7182',"7185",'7186','7188']) ,
                'second_amount':  self.bal_calulator_net_prev(['718']),
                'diff_amount':  self.bal_calulator_net_prev(['718'])   - self.bal_calulator_net_prev(['7181','7182',"7185",'7186','7188']) ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','REPR D\'EXPL : TRANSF DE CH(N) : CPC T2 & T6 DETAIL')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_year(['7191','7192',"7193",'7194','7195','7196','7198','7197']) ,
                'second_amount':  self.bal_calulator_net_year(['719'])  ,
                'diff_amount':  self.bal_calulator_net_year(['719'])  - self.bal_calulator_net_year(['7191','7192',"7193",'7194','7195','7196','7198','7197']) ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','REPR D\'EXPL : TRANSF DE CH(N-1) : CPC T2 & T6 DETAIL')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_prev(['7191','7192',"7193",'7194','7195','7196','7198','7197']) ,
                'second_amount':  self.bal_calulator_net_prev(['719']),
                'diff_amount':  self.bal_calulator_net_prev(['719'])   - self.bal_calulator_net_prev(['7191','7192',"7193",'7194','7195','7196','7198','7197']) ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','ACH REV DE MSES(N) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_year(['6112','6111',"6114"]) ,
                'second_amount':  self.bal_calulator_net_year(['611'])  ,
                'diff_amount':  self.bal_calulator_net_year(['611'])  - self.bal_calulator_net_year(['6112','6111',"6114"]) ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','ACH REV DE MSES(N-1) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_prev(['6112','6111',"6114"]) ,
                'second_amount':  self.bal_calulator_net_prev(['611']),
                'diff_amount':  self.bal_calulator_net_prev(['611'])   - self.bal_calulator_net_prev(['6112','6111',"6114"]) ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','ACH CONS DE MAT&FOUR(N) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_year(['612']) ,
                'second_amount':  self.bal_calulator_net_year(['612'])  ,
                'diff_amount':  0 ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','AUTRE CH EXT(N) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_year(['613','614']) ,
                'second_amount':  self.bal_calulator_net_year(['613','614'])  ,
                'diff_amount':  0 ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','AUTRE CH EXT(N-1) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_prev(['613','614']) ,
                'second_amount':  self.bal_calulator_net_prev(['613','614']),
                'diff_amount': 0,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','CH DE PERSONNEL(N) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_year(['617']) ,
                'second_amount':  self.bal_calulator_net_year(['617'])  ,
                'diff_amount':  0 ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','CH DE PERSONNEL(N-1) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_prev(['617']) ,
                'second_amount':  self.bal_calulator_net_prev(['617']),
                'diff_amount': 0,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','AUT CH D\'EXP(N) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_year(['618']) ,
                'second_amount':  self.bal_calulator_net_year(['618'])  ,
                'diff_amount':  0 ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','AUT CH D\'EXP(N-1) : CPC T2 & T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  self.bal_calulator_net_prev(['618']) ,
                'second_amount':  self.bal_calulator_net_prev(['618']),
                'diff_amount': 0,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','FC : ACTIF & T4 TAB DES IMM')])
            line_22.write({
                'first_amount':self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Fonds commercial'),('company_id','=',self.env.company.id)]).montant_end if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Fonds commercial'),('company_id','=',self.env.company.id)]) else 0 ,
                'second_amount':  self.bal_calulator_current_year(['223']) - self.bal_calulator_current_year(['2823']) ,
                'diff_amount': self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Fonds commercial'),('company_id','=',self.env.company.id)]).montant_end - self.bal_calulator_current_year(['223']) + self.bal_calulator_current_year(['2823']) if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Fonds commercial'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','AUT IMM INCOR : ACTIF & T4 TAB DES IMMO')])
            line_22.write({
                'first_amount':self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Autres immobilisations incorporelles'),('company_id','=',self.env.company.id)]).montant_end if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Autres immobilisations incorporelles'),('company_id','=',self.env.company.id)]) else 0 ,
                'second_amount':  self.bal_calulator_current_year(['228']) - self.bal_calulator_current_year(['2828']) ,
                'diff_amount': self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Autres immobilisations incorporelles'),('company_id','=',self.env.company.id)]).montant_end - self.bal_calulator_current_year(['228']) + self.bal_calulator_current_year(['2828']) if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Autres immobilisations incorporelles'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','TERRAIN : ACTIF & T4 TAB DES IMMO')])
            line_22.write({
                'first_amount':self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Terrains'),('company_id','=',self.env.company.id)]).montant_end if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Terrains'),('company_id','=',self.env.company.id)]) else 0 ,
                'second_amount':  self.bal_calulator_current_year(['231']) - self.bal_calulator_current_year(['2831']) ,
                'diff_amount': self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Terrains'),('company_id','=',self.env.company.id)]).montant_end - self.bal_calulator_current_year(['231']) + self.bal_calulator_current_year(['2831']) if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Terrains'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','CONSTRUCTION : ACTIF & T4 TAB DES IMMO')])
            line_22.write({
                'first_amount':self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Constructions'),('company_id','=',self.env.company.id)]).montant_end if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Constructions'),('company_id','=',self.env.company.id)]) else 0 ,
                'second_amount':  self.bal_calulator_current_year(['232']) - self.bal_calulator_current_year(['2832']) ,
                'diff_amount': self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Constructions'),('company_id','=',self.env.company.id)]).montant_end - self.bal_calulator_current_year(['232']) + self.bal_calulator_current_year(['2832']) if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Constructions'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','INT : ACTIF & TAB DES IMMO')])
            line_22.write({
                'first_amount':self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Installations techniques; matériel et outillage'),('company_id','=',self.env.company.id)]).montant_end if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Installations techniques; matériel et outillage'),('company_id','=',self.env.company.id)]) else 0 ,
                'second_amount':  self.bal_calulator_current_year(['233']) - self.bal_calulator_current_year(['2833']) ,
                'diff_amount': self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Installations techniques; matériel et outillage'),('company_id','=',self.env.company.id)]).montant_end - self.bal_calulator_current_year(['233']) + self.bal_calulator_current_year(['2833']) if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Installations techniques; matériel et outillage'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','MAT TRANSPORT : ACTIF & T4 TAB DES IMMO')])
            line_22.write({
                'first_amount':self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Matériel de transport'),('company_id','=',self.env.company.id)]).montant_end if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Matériel de transport'),('company_id','=',self.env.company.id)]) else 0 ,
                'second_amount':  self.bal_calulator_current_year(['234']) - self.bal_calulator_current_year(['2834']) ,
                'diff_amount': self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Matériel de transport'),('company_id','=',self.env.company.id)]).montant_end - self.bal_calulator_current_year(['234']) + self.bal_calulator_current_year(['2834']) if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Matériel de transport'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','IMMB ET AMENAG : ACTIF & T4 TAB DES IMMO')])
            line_22.write({
                'first_amount':self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Mobilier, matériel de bureau et aménagements'),('company_id','=',self.env.company.id)]).montant_end if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Mobilier, matériel de bureau et aménagements'),('company_id','=',self.env.company.id)]) else 0 ,
                'second_amount':  self.bal_calulator_current_year(['235']) - self.bal_calulator_current_year(['2835']) ,
                'diff_amount': self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Mobilier, matériel de bureau et aménagements'),('company_id','=',self.env.company.id)]).montant_end - self.bal_calulator_current_year(['235']) + self.bal_calulator_current_year(['2835']) if self.env['immo.financiere.line'].search([('immo_id.fy_n_id','=',rec.fy_n_id.id),('name','=','* Mobilier, matériel de bureau et aménagements'),('company_id','=',self.env.company.id)]) else 0 ,
            })
            credit_bail = self.env['credit.bail'].search([('fy_n_id','=',rec.fy_n_id.id),('company_id','=',self.env.company.id)])
            amount = 0
            if credit_bail:
                for line in credit_bail.credit_bail_line_ids:
                    amount += line.monatnt_redevance
            line_22 = self.env['control.table.line'].search([('parent_id','=',rec.id),('name','=','REDEV CREDIT-Bail : T7 TAB DES BIENS CRD-BAIL &  T6 DETAIL CPC')])
            line_22.write({
                'first_amount':  amount ,
                'second_amount': self.bal_calulator_net_year(['6132'])  ,
                'diff_amount':  self.bal_calulator_net_year(['6132'])  - amount ,
            })
            

class ControlTableLine(models.Model):
    _name = 'control.table.line'
    
    name = fields.Char(string='Libelle', readonly=True)
    first_amount = fields.Float(string='Debit')    
    second_amount = fields.Float(string='Credit')    
    diff_amount = fields.Float(string='Solde') 
    parent_id = fields.Many2one(
    comodel_name='control.table'
    ,string = 'Parent'
    ) 
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('control.table.line'))  