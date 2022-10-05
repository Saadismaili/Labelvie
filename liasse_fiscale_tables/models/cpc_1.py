# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
import base64
import zipfile

import os
directory = os.path.dirname(__file__)

class CHARGEPROFIT(models.Model):
    _name = "charge.profit"

    _description = 'TABLEAU de PROFIT'

    name = fields.Char(string=u"Nom",default="Account Report Profit and Loss",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False,store=True,)
    line_ids = fields.One2many(string='Lignes',comodel_name='charge.profit.ligne',inverse_name='parent_id' )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('charge.profit'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    @api.model
    def create(self, values):
        return super(CHARGEPROFIT,self).create({
            'line_ids' : self.env['charge.profit.ligne'].create([{'name':"I. PRODUITS D'EXPLOITATION",'code_edi_current':11176 , 'code_edi_previous':11177 , 'code_edi_net': 11178, 'code_edi_prev_net':11179,'parent_id':self.id,},
                                                                {'name':"* Ventes de marchandises (en l'état)",'code_edi_current':11181 , 'code_edi_previous':11182 , 'code_edi_net': 11183, 'code_edi_prev_net':11184,'parent_id':self.id,},
                                                                {'name':"* Ventes de biens et services produits",'code_edi_current':11186 , 'code_edi_previous':11187 , 'code_edi_net': 11188, 'code_edi_prev_net':11189,'parent_id':self.id,},
                                                                {'name':"* Chiffres d'affaires",'code_edi_current':14021 , 'code_edi_previous':14022 , 'code_edi_net': 14023, 'code_edi_prev_net':14024,'parent_id':self.id,},
                                                                {'name':"* Variation de stocks de produits (1)",'code_edi_current':11191 , 'code_edi_previous':11192 , 'code_edi_net': 11193, 'code_edi_prev_net':11194,'parent_id':self.id,},
                                                                {'name':"* Immobilisations produites par l'entreprise pour elle-même",'code_edi_current':11196 , 'code_edi_previous':11197 , 'code_edi_net': 11198, 'code_edi_prev_net':11199,'parent_id':self.id,},
                                                                {'name':"* Subventions d'exploitation",'code_edi_current':11201 , 'code_edi_previous':11202 , 'code_edi_net': 11203, 'code_edi_prev_net':11204,'parent_id':self.id,},
                                                                {'name':"* Autres produits d'exploitation",'code_edi_current':11206 , 'code_edi_previous':11207 , 'code_edi_net': 11208, 'code_edi_prev_net':11209,'parent_id':self.id,},
                                                                {'name':"* Reprises d'exploitation : transferts de charges",'code_edi_current':11211 , 'code_edi_previous':11212 , 'code_edi_net': 11213, 'code_edi_prev_net':11214,'parent_id':self.id,},
                                                                {'name':"Total I",'code_edi_current':11216 , 'code_edi_previous':11217 , 'code_edi_net': 11218, 'code_edi_prev_net':11219,'parent_id':self.id,},
                                                                {'name':"II. CHARGES D'EXPLOITATION",'code_edi_current':11226 , 'code_edi_previous':11227 , 'code_edi_net': 11228, 'code_edi_prev_net':11229,'parent_id':self.id,},
                                                                {'name':"* Achats revendus(2) de marchandises",'code_edi_current':11221 , 'code_edi_previous':11222 , 'code_edi_net': 11223, 'code_edi_prev_net':11224,'parent_id':self.id,},
                                                                {'name':"* Achats consommés(2) de matières et fournitures",'code_edi_current':11256 , 'code_edi_previous':11257 , 'code_edi_net': 11258, 'code_edi_prev_net':11259,'parent_id':self.id,},
                                                                {'name':"* Autres charges externes",'code_edi_current':11261 , 'code_edi_previous':11262 , 'code_edi_net': 11263, 'code_edi_prev_net':11264,'parent_id':self.id,},
                                                                {'name':"* Impôts et taxes",'code_edi_current':11251 , 'code_edi_previous':11252 , 'code_edi_net': 11253, 'code_edi_prev_net':11254,'parent_id':self.id,},
                                                                {'name':"* Charges de personnel",'code_edi_current':11266 , 'code_edi_previous':11267 , 'code_edi_net': 11268, 'code_edi_prev_net':11269,'parent_id':self.id,},
                                                                {'name':"* Autres charges d'exploitation",'code_edi_current':11246 , 'code_edi_previous':11247 , 'code_edi_net': 11248, 'code_edi_prev_net':11249,'parent_id':self.id,},
                                                                {'name':"* Dotations d'exploitation",'code_edi_current':11241 , 'code_edi_previous':11242 , 'code_edi_net': 11243, 'code_edi_prev_net':11244,'parent_id':self.id,},
                                                                {'name':"Total II",'code_edi_current':11236 , 'code_edi_previous':11237 , 'code_edi_net': 11238, 'code_edi_prev_net':11239,'parent_id':self.id,},
                                                                {'name':"III. RESULTAT D'EXPLOITATION (I-II)",'code_edi_current':11231 , 'code_edi_previous':11232 , 'code_edi_net': 11233, 'code_edi_prev_net':11234,'parent_id':self.id,},
                                                                {'name':"IV. PRODUITS FINANCIERS",'code_edi_current':11326 , 'code_edi_previous':11327 , 'code_edi_net': 11328, 'code_edi_prev_net':11329,'parent_id':self.id,},
                                                                {'name':"* Produits des titres de partic. et autres titres immobilisés",'code_edi_current':11271 , 'code_edi_previous':11272 , 'code_edi_net': 11273, 'code_edi_prev_net':11274,'parent_id':self.id,},
                                                                {'name':"* Gains de change",'code_edi_current':11276 , 'code_edi_previous':11277 , 'code_edi_net': 11278, 'code_edi_prev_net':11279,'parent_id':self.id,},
                                                                {'name':"* Intérêts et autres produits financiers",'code_edi_current':11281 , 'code_edi_previous':11282 , 'code_edi_net': 11283, 'code_edi_prev_net':11284,'parent_id':self.id,},
                                                                {'name':"* Reprises financier : transfert charges",'code_edi_current':11286 , 'code_edi_previous':11287 , 'code_edi_net': 11288, 'code_edi_prev_net':11289,'parent_id':self.id,},
                                                                {'name':"Total IV",'code_edi_current':11291 , 'code_edi_previous':11292 , 'code_edi_net': 11293, 'code_edi_prev_net':11294,'parent_id':self.id,},
                                                                {'name':"V. CHARGES FINANCIERES",'code_edi_current':11321 , 'code_edi_previous':11322 , 'code_edi_net': 11323, 'code_edi_prev_net':11324,'parent_id':self.id,},
                                                                {'name':"* Charges d'intérêts",'code_edi_current':11296 , 'code_edi_previous':11297 , 'code_edi_net': 11298, 'code_edi_prev_net':11299,'parent_id':self.id,},
                                                                {'name':"* Pertes de change",'code_edi_current':11301 , 'code_edi_previous':11302 , 'code_edi_net': 11303, 'code_edi_prev_net':11304,'parent_id':self.id,},
                                                                {'name':"* Autres charges financières",'code_edi_current':11306 , 'code_edi_previous':11307 , 'code_edi_net': 11308, 'code_edi_prev_net':11309,'parent_id':self.id,},
                                                                {'name':"* Dotations financières",'code_edi_current':11311 , 'code_edi_previous':11312 , 'code_edi_net': 11313, 'code_edi_prev_net':11314,'parent_id':self.id,},
                                                                {'name':"Total V",'code_edi_current':11316 , 'code_edi_previous':11317 , 'code_edi_net': 11318, 'code_edi_prev_net':11319,'parent_id':self.id,},
                                                                {'name':"VI. RESULTAT FINANCIER (IV-V)",'code_edi_current':11331 , 'code_edi_previous':11332 , 'code_edi_net': 11333, 'code_edi_prev_net':11334,'parent_id':self.id,},
                                                                {'name':"VII. RESULTAT COURANT (III+VI)",'code_edi_current':11336 , 'code_edi_previous':11337 , 'code_edi_net': 11338, 'code_edi_prev_net':11339,'parent_id':self.id,},
                                                                ]),})
    # this function convert from string to list
    def from_string_to_list(self,val,list):
        list = []
        for x in str(val):
            list.append(x)
        return list
    # this function verify if the code assigned to the line is the same assigned to account move line
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
    # this function returns the Net Current year balance amount of each specific code assigned
    def bal_calulator_current_year(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for entry in journal_entries:
                if rec.fy_n_id:
                    for code in codes:
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
    # this function returns the Net Previous year balance amount of each specific code assigned
    def bal_calulator_previous_years(self,codes):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for entry in journal_entries:
                if rec.fy_n_id:
                    for code in codes:
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

    def get_lines(self):
        for rec in self:
            
            line_2 = self.env['charge.profit.ligne'].search([('name','=',"I. PRODUITS D'EXPLOITATION"),('parent_id','=',rec.id)])
            line_2.write({
            'current':self.bal_calulator_current_year(['711','712','712','711','713','714','716','718','719']) - self.bal_calulator_current_year(['7118','7128','7118','7128','7148','7168','7188','7198']) ,
            'previous':self.bal_calulator_current_year(['7118','7128','7118','7128','7148','7168','7188','7198']) ,
            'net':self.bal_calulator_current_year(['711','712','712','711','713','714','716','718','719']) ,
            'prev_net':self.bal_calulator_previous_years(['711','712','712','711','713','714','716','718','719']) ,
            })

            line_3 = self.env['charge.profit.ligne'].search([('name','=',"* Ventes de marchandises (en l'état)"),('parent_id','=',rec.id)])
            line_3.write({
            'current':self.bal_calulator_current_year(['711']) - self.bal_calulator_current_year(['7118']) ,
            'previous':self.bal_calulator_current_year(['7118']) ,
            'net':self.bal_calulator_current_year(['711']),
            'prev_net':self.bal_calulator_previous_years(['711']) ,
            })
            line_4 = self.env['charge.profit.ligne'].search([('name','=',"* Ventes de biens et services produits"),('parent_id','=',rec.id)])
            line_4.write({
            'current':self.bal_calulator_current_year(['712']) - self.bal_calulator_current_year(['7128']) ,
            'previous':self.bal_calulator_current_year(['7128']) ,
            'net':self.bal_calulator_current_year(['712']) ,
            'prev_net':self.bal_calulator_previous_years(['712']) ,
            })
            line_5 = self.env['charge.profit.ligne'].search([('name','=',"* Chiffres d'affaires"),('parent_id','=',rec.id)])
            line_5.write({
            'current':self.bal_calulator_current_year(['712','711']) - self.bal_calulator_current_year(['7128','7118']) ,
            'previous':self.bal_calulator_current_year(['7128','7118']) ,
            'net':self.bal_calulator_current_year(['712','711']) ,
            'prev_net':self.bal_calulator_previous_years(['712','711']) ,
            })
            line_6 = self.env['charge.profit.ligne'].search([('name','=',"* Variation de stocks de produits (1)"),('parent_id','=',rec.id)])
            line_6.write({
            'current':self.bal_calulator_current_year(['713'])  ,
            'previous':0 ,
            'net':self.bal_calulator_current_year(['713']),
            'prev_net':self.bal_calulator_previous_years(['713']),
            })
            line_7 = self.env['charge.profit.ligne'].search([('name','=',"* Immobilisations produites par l'entreprise pour elle-même"),('parent_id','=',rec.id)])
            line_7.write({
            'current':self.bal_calulator_current_year(['714']) - self.bal_calulator_current_year(['7148']) ,
            'previous':self.bal_calulator_current_year(['7148']) ,
            'net':self.bal_calulator_current_year(['714']) ,
            'prev_net':self.bal_calulator_previous_years(['714']),
            })


            line_8 = self.env['charge.profit.ligne'].search([('name','=',"* Subventions d'exploitation"),('parent_id','=',rec.id)])
            line_8.write({
            'current':self.bal_calulator_current_year(['716']) - self.bal_calulator_current_year(['7168']),
            'previous':self.bal_calulator_current_year(['7168']) ,
            'net':self.bal_calulator_current_year(['716']) ,
            'prev_net':self.bal_calulator_previous_years(['716']) ,
            })
            line_9 = self.env['charge.profit.ligne'].search([('name','=',"* Autres produits d'exploitation"),('parent_id','=',rec.id)])
            line_9.write({
            'current':self.bal_calulator_current_year(['718']) - self.bal_calulator_current_year(['7188']),
            'previous':self.bal_calulator_current_year(['7188']) ,
            'net':self.bal_calulator_current_year(['718']),
            'prev_net':self.bal_calulator_previous_years(['718']),
            })
            line_10 = self.env['charge.profit.ligne'].search([('name','=',"* Reprises d'exploitation : transferts de charges"),('parent_id','=',rec.id)])
            line_10.write({
            'current':self.bal_calulator_current_year(['719']) - self.bal_calulator_current_year(['7198']),
            'previous':self.bal_calulator_current_year(['7198']) ,
            'net':self.bal_calulator_current_year(['719']),
            'prev_net':self.bal_calulator_previous_years(['719']) ,
            })
            line_11 = self.env['charge.profit.ligne'].search([('name','=',"Total I"),('parent_id','=',rec.id)])
            line_11.write({
           'current':self.bal_calulator_current_year(['71']) - self.bal_calulator_current_year(['7118','7128','7148','7168','7188','7198']),
            'previous':self.bal_calulator_current_year(['7118','7128','7148','7168','7188','7198']) ,
            'net':self.bal_calulator_current_year(['71']) ,
            'prev_net':self.bal_calulator_previous_years(['71']),
            })
            line_12 = self.env['charge.profit.ligne'].search([('name','=',"II. CHARGES D'EXPLOITATION"),('parent_id','=',rec.id)])
            line_12.write({
           'current':self.bal_calulator_current_year(['619','611','612','613','614','616','617','618']) - self.bal_calulator_current_year(['6198','6118','6128','6148','6168','6178','6188']),
            'previous':self.bal_calulator_current_year(['6198','6118','6128','6148','6168','6178','6188']) ,
            'net':self.bal_calulator_current_year(['619','611','612','613','614','616','617','618']) ,
            'prev_net':self.bal_calulator_previous_years(['619','611','612','613','614','616','617','618']) ,
            })
            
            line_13 = self.env['charge.profit.ligne'].search([('name','=',"* Achats revendus(2) de marchandises"),('parent_id','=',rec.id)])
            line_13.write({
            'current':self.bal_calulator_current_year(['611']) - self.bal_calulator_current_year(['6118']) ,
            'previous':self.bal_calulator_current_year(['6118']) ,
            'net':self.bal_calulator_current_year(['611']),
            'prev_net':self.bal_calulator_previous_years(['611']) ,
            })

            line_14 = self.env['charge.profit.ligne'].search([('name','=',"* Achats consommés(2) de matières et fournitures"),('parent_id','=',rec.id)])
            line_14.write({
            'current':self.bal_calulator_current_year(['612']) - self.bal_calulator_current_year(['6128']) ,
            'previous':self.bal_calulator_current_year(['6128']) ,
            'net':self.bal_calulator_current_year(['612']) ,
            'prev_net':self.bal_calulator_previous_years(['612']) ,
            })

            line_15 = self.env['charge.profit.ligne'].search([('name','=',"* Autres charges externes"),('parent_id','=',rec.id)])
            line_15.write({
            'current':self.bal_calulator_current_year(['613','614']) - self.bal_calulator_current_year(['6148']),
            'previous':self.bal_calulator_current_year(['6148']) ,
            'net':self.bal_calulator_current_year(['613','614']) ,
            'prev_net':self.bal_calulator_previous_years(['613','614']) ,
            })

            line_1 = self.env['charge.profit.ligne'].search([('name','=',"* Impôts et taxes"),('parent_id','=',rec.id)])
            line_1.write({
            'current':self.bal_calulator_current_year(['616']) - self.bal_calulator_current_year(['6168']) ,
            'previous':self.bal_calulator_current_year(['6168']) ,
            'net':self.bal_calulator_current_year(['616']) ,
            'prev_net':self.bal_calulator_previous_years(['616']) ,
            })

            line_16 = self.env['charge.profit.ligne'].search([('name','=',"* Charges de personnel"),('parent_id','=',rec.id)])
            line_16.write({
           'current':self.bal_calulator_current_year(['617']) - self.bal_calulator_current_year(['6178']) ,
            'previous':self.bal_calulator_current_year(['6178']) ,
            'net':self.bal_calulator_current_year(['617']),
            'prev_net':self.bal_calulator_previous_years(['617']),
            })

            line_17 = self.env['charge.profit.ligne'].search([('name','=',"* Autres charges d'exploitation"),('parent_id','=',rec.id)])
            line_17.write(
            {
            'current':self.bal_calulator_current_year(['618']) - self.bal_calulator_current_year(['6188']) ,
            'previous':self.bal_calulator_current_year(['6188']) ,
            'net':self.bal_calulator_current_year(['618']),
            'prev_net':self.bal_calulator_previous_years(['618']) ,
            })

            line_18 = self.env['charge.profit.ligne'].search([('name','=',"* Dotations d'exploitation"),('parent_id','=',rec.id)])
            line_18.write({
           'current':self.bal_calulator_current_year(['619']) - self.bal_calulator_current_year(['6198']) ,
            'previous':self.bal_calulator_current_year(['6198']) ,
            'net':self.bal_calulator_current_year(['619']) ,
            'prev_net':self.bal_calulator_previous_years(['619']) ,
            })

            line_19 = self.env['charge.profit.ligne'].search([('name','=',"Total II"),('parent_id','=',rec.id)])
            line_19.write({
            'current':self.bal_calulator_current_year(['61']) - self.bal_calulator_current_year(['6118','6128','6168','6178','6188','6198']),
            'previous':self.bal_calulator_current_year(['6118','6128','6168','6178','6188','6198']) ,
            'net':self.bal_calulator_current_year(['61']) ,
            'prev_net':self.bal_calulator_previous_years(['61']),
            })

            line_20 =self.env['charge.profit.ligne'].search([('name','=',"III. RESULTAT D'EXPLOITATION (I-II)"),('parent_id','=',rec.id)])
            line_20.write({
            'current':line_11.current - line_19.current ,
            'previous':line_11.previous - line_19.previous ,
            'net':line_11.net - line_19.net,
            'prev_net':line_11.prev_net - line_19.prev_net,
            })
            line_21 = self.env['charge.profit.ligne'].search([('name','=',"IV. PRODUITS FINANCIERS"),('parent_id','=',rec.id)])
            line_21.write({
            'current':self.bal_calulator_current_year(['732','733','738','739']) - self.bal_calulator_current_year(['7328','7338','7388','7398']),
            'previous':self.bal_calulator_current_year(['7328','7338','7388','7398']) ,
            'net':self.bal_calulator_current_year(['732','733','738','739']) ,
            'prev_net':self.bal_calulator_previous_years(['732','733','738','739']) ,
            })
            line_22 = self.env['charge.profit.ligne'].search([('name','=',"* Produits des titres de partic. et autres titres immobilisés"),('parent_id','=',rec.id)])
            line_22.write({
            'current':self.bal_calulator_current_year(['732']) - self.bal_calulator_current_year(['7328']) ,
            'previous':self.bal_calulator_current_year(['7328']) ,
            'net':self.bal_calulator_current_year(['732']),
            'prev_net':self.bal_calulator_previous_years(['732']) ,
            })
            line_23 = self.env['charge.profit.ligne'].search([('name','=',"* Gains de change"),('parent_id','=',rec.id)])
            line_23.write({
            'current':self.bal_calulator_current_year(['733']) - self.bal_calulator_current_year(['7338']) ,
            'previous':self.bal_calulator_current_year(['7338']) ,
            'net':self.bal_calulator_current_year(['733']),
            'prev_net':self.bal_calulator_previous_years(['733']) ,
            })
            line_24 = self.env['charge.profit.ligne'].search([('name','=',"* Intérêts et autres produits financiers"),('parent_id','=',rec.id)])
            line_24.write({
            'current':self.bal_calulator_current_year(['738']) - self.bal_calulator_current_year(['7388']) ,
            'previous':self.bal_calulator_current_year(['7388']) ,
            'net':self.bal_calulator_current_year(['738']),
            'prev_net':self.bal_calulator_previous_years(['738']),
            })
            line_25 = self.env['charge.profit.ligne'].search([('name','=',"* Reprises financier : transfert charges"),('parent_id','=',rec.id)])
            line_25.write({
            'current':self.bal_calulator_current_year(['739']) - self.bal_calulator_current_year(['7398']) ,
            'previous':self.bal_calulator_current_year(['7398']) ,
            'net':self.bal_calulator_current_year(['739']) ,
            'prev_net':self.bal_calulator_previous_years(['739']) ,
            })
            line_26 = self.env['charge.profit.ligne'].search([('name','=',"Total IV"),('parent_id','=',rec.id)])
            line_26.write({
            'current':self.bal_calulator_current_year(['73']) - self.bal_calulator_current_year(['7328','7338','7388','7398']),
            'previous':self.bal_calulator_current_year(['7328','7338','7388','7398']) ,
            'net':self.bal_calulator_current_year(['73']),
            'prev_net':self.bal_calulator_previous_years(['73']) ,
            })
            line_27 = self.env['charge.profit.ligne'].search([('name','=',"V. CHARGES FINANCIERES"),('parent_id','=',rec.id)])
            line_27.write({
           'current':self.bal_calulator_current_year(['631','633','638','639']) - self.bal_calulator_current_year(['6318','6338','6388','6398']),
            'previous':self.bal_calulator_current_year(['6318','6338','6388','6398']) ,
            'net':self.bal_calulator_current_year(['631','633','638','639']) ,
            'prev_net':self.bal_calulator_previous_years(['631','633','638','639']) ,
            })
            line_28 = self.env['charge.profit.ligne'].search([('name','=',"* Charges d'intérêts"),('parent_id','=',rec.id)])
            line_28.write({
            'current':self.bal_calulator_current_year(['631']) - self.bal_calulator_current_year(['6318']) ,
            'previous':self.bal_calulator_current_year(['6318']) ,
            'net':self.bal_calulator_current_year(['631']) ,
            'prev_net':self.bal_calulator_previous_years(['631']) ,
            })
            line_29 = self.env['charge.profit.ligne'].search([('name','=',"* Pertes de change"),('parent_id','=',rec.id)])
            line_29.write({
            'current':self.bal_calulator_current_year(['633']) - self.bal_calulator_current_year(['6338']) ,
            'previous':self.bal_calulator_current_year(['6338']) ,
            'net':self.bal_calulator_current_year(['633']) ,
            'prev_net':self.bal_calulator_previous_years(['633']),
            })
            line_30 = self.env['charge.profit.ligne'].search([('name','=',"* Autres charges financières"),('parent_id','=',rec.id)])
            line_30.write({
            'current':self.bal_calulator_current_year(['638']) - self.bal_calulator_current_year(['6388']) ,
            'previous':self.bal_calulator_current_year(['6388']) ,
            'net':self.bal_calulator_current_year(['638']) ,
            'prev_net':self.bal_calulator_previous_years(['638']),
            })
            line_31 = self.env['charge.profit.ligne'].search([('name','=',"* Dotations financières"),('parent_id','=',rec.id)])
            line_31.write({
            'current':self.bal_calulator_current_year(['639']) - self.bal_calulator_current_year(['6398']) ,
            'previous':self.bal_calulator_current_year(['6398']) ,
            'net':self.bal_calulator_current_year(['639']) ,
            'prev_net':self.bal_calulator_previous_years(['639']) ,
            })
            line_32 = self.env['charge.profit.ligne'].search([('name','=',"Total V"),('parent_id','=',rec.id)])
            line_32.write({
            'current':self.bal_calulator_current_year(['63']) - self.bal_calulator_current_year(['6318','6338','6388','6388','6398']),
            'previous':self.bal_calulator_current_year(['6318','6338','6388','6388','6398']) ,
            'net':self.bal_calulator_current_year(['63']) ,
            'prev_net':self.bal_calulator_previous_years(['63']) ,
            })
            line_33 = self.env['charge.profit.ligne'].search([('name','=',"VI. RESULTAT FINANCIER (IV-V)"),('parent_id','=',rec.id)])
            line_33.write({
            'current':line_26.current - line_32.current ,
            'previous':line_26.previous - line_32.previous ,
            'net':line_26.net - line_32.net,
            'prev_net':line_26.prev_net - line_32.prev_net,
            })
            line_34 = self.env['charge.profit.ligne'].search([('name','=',"VII. RESULTAT COURANT (III+VI)"),('parent_id','=',rec.id)])
            line_34.write({
            'current':line_20.current + line_33.current ,
            'previous':line_20.previous + line_33.previous ,
            'net':line_20.net + line_33.net,
            'prev_net':line_20.prev_net + line_33.prev_net,
            })
    
    def get_xml(self,parent):
        pass

class CHARGEPROFITLignes(models.Model):
    _name = "charge.profit.ligne"  

    name = fields.Char(string=u"Nom",required=True,readonly=True)
    current  = fields.Float(string=u"Propres à l\'exercice",readonly=True)
    previous  = fields.Float(string=u"Concernant les exercices précédents",readonly=True)
    net  = fields.Float(string=u"Net d'exercice précédent",readonly=True)
    prev_net  = fields.Float(string=u"Net d'exercice précédent",readonly=True)
    
    # Code edis
    code_edi_current = fields.Integer(string='Edi Propres',readonly=True)
    code_edi_previous = fields.Integer(string='Edi précédents',readonly=True)
    code_edi_net = fields.Integer(string='Edi Net',readonly=True)
    code_edi_prev_net = fields.Integer(string='Edi Prev Net',readonly=True)
    
    # relational fields
    parent_id = fields.Many2one(string='Parent Id', comodel_name='charge.profit')
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('charge.profit.ligne'))



