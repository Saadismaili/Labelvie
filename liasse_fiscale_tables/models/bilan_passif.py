# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile

import os
directory = os.path.dirname(__file__)

class BilanPassive(models.Model):
    _name = "bilan.passive"

    _description = 'TABLEAU de Bilan Passive'

    name = fields.Char(string=u"Nom",default="Bilan Passive",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False,store=True,)
    line_ids = fields.One2many(string='Lignes',comodel_name='bilan.passive.ligne',inverse_name='bilan_id' )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('bilan.passive'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    @api.model
    def create(self, values):
        return super(BilanPassive,self).create({
            'line_ids' : self.env['bilan.passive.ligne'].create([{'name':'CAPITAUX PROPRES','bilan_id':self.id,},
                                                                  {'name':'* Capital social ou personnel (1)','code_edi_net':13400 , 'code_edi_prev_net': 13411,'bilan_id':self.id,},
                                                                  {'name':'* Moins : actionnaires, capital souscrit non appelé','code_edi_net':13401 , 'code_edi_prev_net': 13412,'bilan_id':self.id,},
                                                                  {'name':'Share Equity (Virtual)','bilan_id':self.id,},
                                                                  {'name':'* Moins : capital appelé','code_edi_net':13402 , 'code_edi_prev_net': 13413,'bilan_id':self.id,},
                                                                  {'name':'* Moins : Dont versé','code_edi_net':13403 , 'code_edi_prev_net': 13414,'bilan_id':self.id,},
                                                                  {'name':'* Prime d\'émission, de fusion, d\'apport','code_edi_net':13404 , 'code_edi_prev_net': 13415,'bilan_id':self.id,},
                                                                  {'name':'* Ecarts de réevaluation','code_edi_net':13405 , 'code_edi_prev_net': 13416,'bilan_id':self.id,},
                                                                  {'name':'* Réserve légale','code_edi_net':13406 , 'code_edi_prev_net': 13417,'bilan_id':self.id,},
                                                                  {'name':'* Autres réserves','code_edi_net':13407 , 'code_edi_prev_net': 13418,'bilan_id':self.id,},
                                                                  {'name':'* Report à nouveau (2)','code_edi_net':13408 , 'code_edi_prev_net': 13419,'bilan_id':self.id,},
                                                                  {'name':'* Résultat nets en instance d\'affectation (2)','code_edi_net':14001 , 'code_edi_prev_net': 14002,'bilan_id':self.id,},
                                                                  {'name':'* Résultat net de l\'exercice (2)','code_edi_net':13409 , 'code_edi_prev_net': 13420,'bilan_id':self.id,},
                                                                  {'name':'TOTAL DES CAPITAUX PROPRES (A)','code_edi_net':13410 , 'code_edi_prev_net': 13421,'bilan_id':self.id,},
                                                                  {'name':'CAPITAUX PROPRES ASSIMILES (B)','code_edi_net':13397 , 'code_edi_prev_net': 13422,'bilan_id':self.id,},
                                                                  {'name':'* Subvention d\'investissement','code_edi_net':13398 , 'code_edi_prev_net': 13423,'bilan_id':self.id,},
                                                                  {'name':'* Provisions réglementées','code_edi_net':13399 , 'code_edi_prev_net': 13424,'bilan_id':self.id,},
                                                                  {'name':'DETTES DE FINANCEMENT (C)','code_edi_net':13393 , 'code_edi_prev_net': 13426,'bilan_id':self.id,},
                                                                  {'name':'* Emprunts obligataires','code_edi_net':13394 , 'code_edi_prev_net': 13427,'bilan_id':self.id,},
                                                                  {'name':'* Autres dettes de financement','code_edi_net':13395 , 'code_edi_prev_net': 13428,'bilan_id':self.id,},
                                                                  {'name':'PROVISIONS DURABLES POUR RISQUES ET CHARGES (D)','code_edi_net':13389 , 'code_edi_prev_net': 13430,'bilan_id':self.id,},
                                                                  {'name':'* Provisions pour risques','code_edi_net':13390 , 'code_edi_prev_net': 13431,'bilan_id':self.id,},
                                                                  {'name':'* Provisions pour charges','code_edi_net':13391 , 'code_edi_prev_net': 13432,'bilan_id':self.id,},
                                                                  {'name':'ECARTS DE CONVERSION - PASSIF (E)','code_edi_net':13386 , 'code_edi_prev_net': 13433,'bilan_id':self.id,},
                                                                  {'name':'* Augmentation des créances immobilisées','code_edi_net':13387 , 'code_edi_prev_net': 13434,'bilan_id':self.id,},
                                                                  {'name':'* Diminution des dettes de financement','code_edi_net':13388 , 'code_edi_prev_net': 13435,'bilan_id':self.id,},
                                                                  {'name':'TOTAL I (A+B+C+D+E)','code_edi_net':13385 , 'code_edi_prev_net': 13436,'bilan_id':self.id,},
                                                                  {'name':'DETTES DU PASSIF CIRCULANT (F)','code_edi_net':13376 , 'code_edi_prev_net': 13437,'bilan_id':self.id,},
                                                                  {'name':'* Fournisseurs et comptes rattachés','code_edi_net':13377 , 'code_edi_prev_net': 13438,'bilan_id':self.id,},
                                                                  {'name':'* Clients créditeurs, avances et acomptes','code_edi_net':13378 , 'code_edi_prev_net': 13439,'bilan_id':self.id,},
                                                                  {'name':'* Personnel','code_edi_net':13379 , 'code_edi_prev_net': 13440,'bilan_id':self.id,},
                                                                  {'name':'* Organisme sociaux','code_edi_net':13380 , 'code_edi_prev_net': 13441,'bilan_id':self.id,},
                                                                  {'name':'* Etat','code_edi_net':13381 , 'code_edi_prev_net': 13442,'bilan_id':self.id,},
                                                                  {'name':'* Comptes d\'associés','code_edi_net':13382 , 'code_edi_prev_net': 13443,'bilan_id':self.id,},
                                                                  {'name':'* Autres créanciers','code_edi_net':13383 , 'code_edi_prev_net': 13444,'bilan_id':self.id,},
                                                                  {'name':'* Comptes de regularisation passif','code_edi_net':13384 , 'code_edi_prev_net': 13445,'bilan_id':self.id,},
                                                                  {'name':'AUTRES PROVISIONS POUR RISQUES ET CHARGES (G)','code_edi_net':13375 , 'code_edi_prev_net': 13446,'bilan_id':self.id,},
                                                                  {'name':'ECARTS DE CONVERSION-PASSIF (Elements circulants) (H)','code_edi_net':13374 , 'code_edi_prev_net': 13447,'bilan_id':self.id,},
                                                                  {'name':'TOTAL II (F+G+H)','code_edi_net':13373 , 'code_edi_prev_net': 13448,'bilan_id':self.id,},
                                                                  {'name':'TRESORERIE-PASSIF', 'bilan_id':self.id,},
                                                                  {'name':'* Crédits d\'escompte','code_edi_net':13370 , 'code_edi_prev_net': 13449,'bilan_id':self.id,},
                                                                  {'name':'* Crédits de trésorerie','code_edi_net':13371 , 'code_edi_prev_net': 13450,'bilan_id':self.id,},
                                                                  {'name':'* Banques (soldes créditeurs)','code_edi_net':13372 , 'code_edi_prev_net': 13451,'bilan_id':self.id,},
                                                                  {'name':'TOTAL III','code_edi_net':13369 , 'code_edi_prev_net': 13452,'bilan_id':self.id,},
                                                                  {'name':'TOTAL GENERAL (I+II+III)','code_edi_net':13368 , 'code_edi_prev_net': 13453,'bilan_id':self.id,},
                                                                 
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
        
    def get_xml(self,parent):
        for rec in self:
            if rec.line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(1) #specific id of table dont change it (read documentation xml)
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                for line in rec.line_ids:
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_net)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.net)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_prev_net)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.prev_net)
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
            else:
                pass
    # this function returns the Current year balance amount of each specific code assigned
    def bal_calulator_current_year(self,code):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for entry in journal_entries:
                if rec.fy_n_id:
                    for ref in rec.fy_n_id:
                        for item in entry.line_ids:
                            if (ref.date_end.year) >= entry.date.year:
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
    # this function returns the Net current year balance amount of each specific code assigned
    def bal_calulator_net_year(self,code):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
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
        
    # this function returns the Net previous year balance amount of each specific code assigned
    def bal_calulator_net_prev(self,code):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for entry in journal_entries:
                if rec.fy_n_id:
                    for ref in rec.fy_n_id:
                        for item in entry.line_ids:
                            if ref.date_end.year - 1 == entry.date.year :
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

    # this function returns the previous year balance amount of each specific code assigned
    def bal_calulator_previous_years(self,code):
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for entry in journal_entries:
                if rec.fy_n_id:
                    for ref in rec.fy_n_id:
                        for item in entry.line_ids:
                            if ref.date_end.year > (entry.date.year):
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
            line_1 = self.env['bilan.passive.ligne'].search([('name','=','* Capital social ou personnel (1)'),('bilan_id','=',rec.id)])
            line_1.write({
            'net':self.bal_calulator_current_year('1111') ,
            'prev_net':self.bal_calulator_previous_years('1111'),
            })
            line_2 = self.env['bilan.passive.ligne'].search([('name','=','* Moins : actionnaires, capital souscrit non appelé'),('bilan_id','=',rec.id)])
            line_2.write({
            'net':self.bal_calulator_current_year('1119'),
            'prev_net':self.bal_calulator_previous_years('1119'),
            })
            line_3 = self.env['bilan.passive.ligne'].search([('name','=','* Moins : capital appelé'),('bilan_id','=',rec.id)])
            line_3.write({
            # 'net':self.bal_calulator_current_year('1111'),
            # 'prev_net':self.bal_calulator_previous_years('1111'),
            })
            line_4 = self.env['bilan.passive.ligne'].search([('name','=','* Moins : Dont versé'),('bilan_id','=',rec.id)])
            line_4.write({
            # 'net':self.bal_calulator_current_year('1111'),
            # 'prev_net':self.bal_calulator_previous_years('1111'),
            })
            line_5 = self.env['bilan.passive.ligne'].search([('name','=','* Prime d\'émission, de fusion, d\'apport'),('bilan_id','=',rec.id)])
            line_5.write({
            'net':self.bal_calulator_current_year('112') ,
            'prev_net':self.bal_calulator_previous_years('112'),
            })
            line_6 = self.env['bilan.passive.ligne'].search([('name','=','* Ecarts de réevaluation'),('bilan_id','=',rec.id)])
            line_6.write({
            'net':self.bal_calulator_current_year('113'),
            'prev_net':self.bal_calulator_previous_years('113'),
            })
            line_7 = self.env['bilan.passive.ligne'].search([('name','=','* Réserve légale'),('bilan_id','=',rec.id)])
            line_7.write({
            'net':self.bal_calulator_current_year('114') ,
            'prev_net':self.bal_calulator_previous_years('114'),
            })
            line_8 = self.env['bilan.passive.ligne'].search([('name','=','* Autres réserves'),('bilan_id','=',rec.id)])
            line_8.write({
            'net':self.bal_calulator_current_year('115'),
            'prev_net':self.bal_calulator_previous_years('115'),
            })
            line_9 = self.env['bilan.passive.ligne'].search([('name','=','* Report à nouveau (2)'),('bilan_id','=',rec.id)])
            line_9.write({
            'net':self.bal_calulator_current_year('116'),
            'prev_net':self.bal_calulator_previous_years('116'),
            })
            line_10 = self.env['bilan.passive.ligne'].search([('name','=','* Résultat nets en instance d\'affectation (2)'),('bilan_id','=',rec.id)])
            line_10.write({
            'net':self.bal_calulator_current_year('118'),
            'prev_net':self.bal_calulator_previous_years('118'),
            })
            line_11 = self.env['bilan.passive.ligne'].search([('name','=','* Résultat net de l\'exercice (2)'),('bilan_id','=',rec.id)])
            line_11.write({
            'net':self.bal_calulator_net_year('71') - self.bal_calulator_net_year('61')+self.bal_calulator_net_year('73') -self.bal_calulator_net_year('63')+self.bal_calulator_net_year('75') -self.bal_calulator_net_year('65')-self.bal_calulator_net_year('67'),
            'prev_net':self.bal_calulator_net_prev('71') - self.bal_calulator_net_prev('61')+self.bal_calulator_net_prev('73') -self.bal_calulator_net_prev('63')+self.bal_calulator_net_prev('75') -self.bal_calulator_net_prev('65')-self.bal_calulator_net_prev('67'),
            })
            line_12 = self.env['bilan.passive.ligne'].search([('name','=','CAPITAUX PROPRES'),('bilan_id','=',rec.id)])
            line_12.write({
            'net':self.bal_calulator_current_year('1111')+self.bal_calulator_current_year('1119')+self.bal_calulator_current_year('112')+self.bal_calulator_current_year('113')+self.bal_calulator_current_year('114')+self.bal_calulator_current_year('115')+self.bal_calulator_current_year('116')+ self.bal_calulator_current_year('118')+ self.bal_calulator_net_year('71') - self.bal_calulator_net_year('61')+self.bal_calulator_net_year('73') - self.bal_calulator_net_year('63')+self.bal_calulator_net_year('75') - self.bal_calulator_net_year('65')-self.bal_calulator_net_year('67') ,
            'prev_net':self.bal_calulator_previous_years('1111')+self.bal_calulator_previous_years('1119')+self.bal_calulator_previous_years('112')+self.bal_calulator_previous_years('113')+self.bal_calulator_previous_years('114')+self.bal_calulator_previous_years('115')+self.bal_calulator_previous_years('116')+ self.bal_calulator_previous_years('118')+ self.bal_calulator_net_prev('71') - self.bal_calulator_net_prev('61')+self.bal_calulator_net_prev('73') - self.bal_calulator_net_prev('63')+self.bal_calulator_net_prev('75') - self.bal_calulator_net_prev('65')-self.bal_calulator_net_prev('67') ,
            })

            line_13 = self.env['bilan.passive.ligne'].search([('name','=','TOTAL DES CAPITAUX PROPRES (A)'),('bilan_id','=',rec.id)])
            line_13.write({
            'net':self.bal_calulator_current_year('1111')+self.bal_calulator_current_year('1119')+self.bal_calulator_current_year('112')+self.bal_calulator_current_year('113')+self.bal_calulator_current_year('114')+self.bal_calulator_current_year('115')+self.bal_calulator_current_year('116')+ self.bal_calulator_current_year('118')+ self.bal_calulator_net_year('71') - self.bal_calulator_net_year('61')+self.bal_calulator_net_year('73') - self.bal_calulator_net_year('63')+self.bal_calulator_net_year('75') - self.bal_calulator_net_year('65')-self.bal_calulator_net_year('67') ,
            'prev_net':self.bal_calulator_previous_years('1111')+self.bal_calulator_previous_years('1119')+self.bal_calulator_previous_years('112')+self.bal_calulator_previous_years('113')+self.bal_calulator_previous_years('114')+self.bal_calulator_previous_years('115')+self.bal_calulator_previous_years('116')+ self.bal_calulator_previous_years('118')+ self.bal_calulator_net_prev('71') - self.bal_calulator_net_prev('61')+self.bal_calulator_net_prev('73') - self.bal_calulator_net_prev('63')+self.bal_calulator_net_prev('75') - self.bal_calulator_net_prev('65')-self.bal_calulator_net_prev('67') ,
            })

            line_14 = self.env['bilan.passive.ligne'].search([('name','=','* Subvention d\'investissement'),('bilan_id','=',rec.id)])
            line_14.write({
            'net':self.bal_calulator_current_year('131') ,
            'prev_net':self.bal_calulator_previous_years('131'),
            })
            line_15 = self.env['bilan.passive.ligne'].search([('name','=','* Provisions réglementées'),('bilan_id','=',rec.id)])
            line_15.write({
            'net':self.bal_calulator_current_year('135') ,
            'prev_net':self.bal_calulator_previous_years('135'),
            })
            line_16 = self.env['bilan.passive.ligne'].search([('name','=','CAPITAUX PROPRES ASSIMILES (B)'),('bilan_id','=',rec.id)])
            line_16.write({
            'net':self.bal_calulator_current_year('135') + self.bal_calulator_current_year('131'),
            'prev_net':self.bal_calulator_previous_years('135') + self.bal_calulator_previous_years('131'),
            })


            line_17 = self.env['bilan.passive.ligne'].search([('name','=','* Emprunts obligataires'),('bilan_id','=',rec.id)])
            line_17.write(
            {'net':self.bal_calulator_current_year('141') ,
            'prev_net':self.bal_calulator_previous_years('141'),
            })
            line_18 = self.env['bilan.passive.ligne'].search([('name','=','* Autres dettes de financement'),('bilan_id','=',rec.id)])
            line_18.write({
            'net':self.bal_calulator_current_year('148'),
            'prev_net':self.bal_calulator_previous_years('148'),
            })
            line_19 = self.env['bilan.passive.ligne'].search([('name','=','DETTES DE FINANCEMENT (C)'),('bilan_id','=',rec.id)])
            line_19.write({
            'net':self.bal_calulator_current_year('148')+self.bal_calulator_current_year('141'),
            'prev_net':self.bal_calulator_previous_years('148')+self.bal_calulator_previous_years('141'),
            })

            line_20 = self.env['bilan.passive.ligne'].search([('name','=','* Provisions pour risques'),('bilan_id','=',rec.id)])
            line_20.write({
            'net':self.bal_calulator_current_year('151'),
            'prev_net':self.bal_calulator_previous_years('151'),
            })
            line_21 = self.env['bilan.passive.ligne'].search([('name','=','* Provisions pour charges'),('bilan_id','=',rec.id)])
            line_21.write({
            'net':self.bal_calulator_current_year('155') ,
            'prev_net':self.bal_calulator_previous_years('155'),
            })
            line_22 = self.env['bilan.passive.ligne'].search([('name','=','PROVISIONS DURABLES POUR RISQUES ET CHARGES (D)'),('bilan_id','=',rec.id)])
            line_22.write({
            'net':self.bal_calulator_current_year('151') + self.bal_calulator_current_year('155'),
            'prev_net':self.bal_calulator_previous_years('151') + self.bal_calulator_previous_years('155'),
            })

            line_23 = self.env['bilan.passive.ligne'].search([('name','=','* Augmentation des créances immobilisées'),('bilan_id','=',rec.id)])
            line_23.write({
            'net':self.bal_calulator_current_year('171'),
            'prev_net':self.bal_calulator_previous_years('171'),
            })
            line_24 = self.env['bilan.passive.ligne'].search([('name','=','* Diminution des dettes de financement'),('bilan_id','=',rec.id)])
            line_24.write({'net':self.bal_calulator_current_year('172'),
            'prev_net':self.bal_calulator_previous_years('172'),
            })
            line_25 = self.env['bilan.passive.ligne'].search([('name','=','ECARTS DE CONVERSION - PASSIF (E)'),('bilan_id','=',rec.id)])
            line_25.write({
            'net':self.bal_calulator_current_year('171') + self.bal_calulator_current_year('172'),
            'prev_net':self.bal_calulator_previous_years('171') + self.bal_calulator_previous_years('172'),
            })

            line_26 = self.env['bilan.passive.ligne'].search([('name','=','TOTAL I (A+B+C+D+E)'),('bilan_id','=',rec.id)])
            line_26.write({
            'net':self.bal_calulator_current_year('171') + self.bal_calulator_current_year('1111')+self.bal_calulator_current_year('1119')+self.bal_calulator_current_year('112')+self.bal_calulator_current_year('113')+self.bal_calulator_current_year('114')+self.bal_calulator_current_year('115')+self.bal_calulator_current_year('116')+ self.bal_calulator_current_year('118')+ self.bal_calulator_net_year('71') - self.bal_calulator_net_year('61')+self.bal_calulator_net_year('73') - self.bal_calulator_net_year('63')+self.bal_calulator_net_year('75') - self.bal_calulator_net_year('65')-self.bal_calulator_net_year('67') +self.bal_calulator_current_year('172')+self.bal_calulator_current_year('151') + self.bal_calulator_current_year('155') + self.bal_calulator_current_year('148')+self.bal_calulator_current_year('141') + self.bal_calulator_current_year('135') + self.bal_calulator_current_year('131'),
            'prev_net':self.bal_calulator_previous_years('171') + self.bal_calulator_previous_years('1111')+self.bal_calulator_previous_years('1119')+self.bal_calulator_previous_years('112')+self.bal_calulator_previous_years('113')+self.bal_calulator_previous_years('114')+self.bal_calulator_previous_years('115')+self.bal_calulator_previous_years('116')+ self.bal_calulator_previous_years('118')+ self.bal_calulator_net_prev('71') - self.bal_calulator_net_prev('61')+self.bal_calulator_net_prev('73') - self.bal_calulator_net_prev('63')+self.bal_calulator_net_prev('75') - self.bal_calulator_net_prev('65')-self.bal_calulator_net_prev('67') +self.bal_calulator_previous_years('172')+self.bal_calulator_previous_years('151') + self.bal_calulator_previous_years('155') + self.bal_calulator_previous_years('148')+self.bal_calulator_previous_years('141') + self.bal_calulator_previous_years('135') + self.bal_calulator_previous_years('131'),
            })

            line_27 = self.env['bilan.passive.ligne'].search([('name','=','* Fournisseurs et comptes rattachés'),('bilan_id','=',rec.id)])
            line_27.write({
            'net':self.bal_calulator_current_year('441') ,
            'prev_net':self.bal_calulator_previous_years('441') ,
            })
            line_28 = self.env['bilan.passive.ligne'].search([('name','=','* Clients créditeurs, avances et acomptes'),('bilan_id','=',rec.id)])
            line_28.write({
            'net': self.bal_calulator_current_year('442'),
            'prev_net': self.bal_calulator_previous_years('442'),
            })
            line_29 = self.env['bilan.passive.ligne'].search([('name','=','* Personnel'),('bilan_id','=',rec.id)])
            line_29.write({
            'net':self.bal_calulator_current_year('443'),
            'prev_net':self.bal_calulator_previous_years('443'),
            })
            line_30 = self.env['bilan.passive.ligne'].search([('name','=','* Organisme sociaux'),('bilan_id','=',rec.id)])
            line_30.write({
            'net':self.bal_calulator_current_year('444'),
            'prev_net':self.bal_calulator_previous_years('444'),
            })
            line_31 = self.env['bilan.passive.ligne'].search([('name','=','* Etat'),('bilan_id','=',rec.id)])
            line_31.write({
            'net':self.bal_calulator_current_year('445'),
            'prev_net':self.bal_calulator_previous_years('445') ,
            })
            line_32 = self.env['bilan.passive.ligne'].search([('name','=','* Comptes d\'associés'),('bilan_id','=',rec.id)])
            line_32.write({
            'net':self.bal_calulator_current_year('446'),
            'prev_net':self.bal_calulator_previous_years('446') ,
            })
            line_34 = self.env['bilan.passive.ligne'].search([('name','=','* Autres créanciers'),('bilan_id','=',rec.id)])
            line_34.write({
            'net':self.bal_calulator_current_year('448'),
            'prev_net':self.bal_calulator_previous_years('448'),
            })
            line_35 = self.env['bilan.passive.ligne'].search([('name','=','* Comptes de regularisation passif'),('bilan_id','=',rec.id)])
            line_35.write({
            'net':self.bal_calulator_current_year('449'),
            'prev_net':self.bal_calulator_previous_years('449'),
            })
            line_36 = self.env['bilan.passive.ligne'].search([('name','=','DETTES DU PASSIF CIRCULANT (F)'),('bilan_id','=',rec.id)])
            line_36.write({
            'net':self.bal_calulator_current_year('446')+self.bal_calulator_current_year('442')+self.bal_calulator_current_year('441')+self.bal_calulator_current_year('443')+self.bal_calulator_current_year('444')+self.bal_calulator_current_year('445') +self.bal_calulator_current_year('449')+self.bal_calulator_current_year('448'),
            'prev_net':self.bal_calulator_previous_years('446')+self.bal_calulator_previous_years('442')+self.bal_calulator_previous_years('441')+self.bal_calulator_previous_years('443')+self.bal_calulator_previous_years('444')+self.bal_calulator_previous_years('445') +self.bal_calulator_previous_years('449')+self.bal_calulator_previous_years('448'),
            })

            line_37 = self.env['bilan.passive.ligne'].search([('name','=','AUTRES PROVISIONS POUR RISQUES ET CHARGES (G)'),('bilan_id','=',rec.id)])
            line_37.write({
            'net': self.bal_calulator_current_year('450') ,
            'prev_net': self.bal_calulator_previous_years('450') ,
            })

            line_38 = self.env['bilan.passive.ligne'].search([('name','=','ECARTS DE CONVERSION-PASSIF (Elements circulants) (H)'),('bilan_id','=',rec.id)])
            line_38.write({
            'net':self.bal_calulator_current_year('470'),
            'prev_net':self.bal_calulator_previous_years('470'),
            })

            line_39 = self.env['bilan.passive.ligne'].search([('name','=','TOTAL II (F+G+H)'),('bilan_id','=',rec.id)])
            line_39.write({
            'net':self.bal_calulator_current_year('470')+self.bal_calulator_current_year('450')+self.bal_calulator_current_year('446')+self.bal_calulator_current_year('442')+self.bal_calulator_current_year('441')+self.bal_calulator_current_year('443')+self.bal_calulator_current_year('444')+self.bal_calulator_current_year('445') +self.bal_calulator_current_year('449')+self.bal_calulator_current_year('448'),
            'prev_net':self.bal_calulator_previous_years('470')+self.bal_calulator_previous_years('450')+self.bal_calulator_previous_years('446')+self.bal_calulator_previous_years('442')+self.bal_calulator_previous_years('441')+self.bal_calulator_previous_years('443')+self.bal_calulator_previous_years('444')+self.bal_calulator_previous_years('445') +self.bal_calulator_previous_years('449')+self.bal_calulator_previous_years('448'),
            })

            line_40 = self.env['bilan.passive.ligne'].search([('name','=','* Crédits d\'escompte'),('bilan_id','=',rec.id)])
            line_40.write({
            'net':self.bal_calulator_current_year('552'),
            'prev_net':self.bal_calulator_previous_years('552'),
            })
            line_41 = self.env['bilan.passive.ligne'].search([('name','=','* Crédits de trésorerie'),('bilan_id','=',rec.id)])
            line_41.write({
            'net':self.bal_calulator_current_year('553'),
            'prev_net':self.bal_calulator_previous_years('553'),
            })
            line_42 = self.env['bilan.passive.ligne'].search([('name','=','* Banques (soldes créditeurs)'),('bilan_id','=',rec.id)])
            line_42.write({
            'net':self.bal_calulator_current_year('554'),
            'prev_net':self.bal_calulator_previous_years('554'),
            })
            line_43 = self.env['bilan.passive.ligne'].search([('name','=','TRESORERIE-PASSIF'),('bilan_id','=',rec.id)])
            line_43.write({
            'net':self.bal_calulator_current_year('554')+self.bal_calulator_current_year('553')+self.bal_calulator_current_year('552'),
            'prev_net':self.bal_calulator_previous_years('554')+self.bal_calulator_previous_years('553')+self.bal_calulator_previous_years('552'),
            })

            line_44 = self.env['bilan.passive.ligne'].search([('name','=','TOTAL III'),('bilan_id','=',rec.id)])
            line_44.write({
            'net':self.bal_calulator_current_year('554')+self.bal_calulator_current_year('553')+self.bal_calulator_current_year('552'),
            'prev_net':self.bal_calulator_previous_years('554')+self.bal_calulator_previous_years('553')+self.bal_calulator_previous_years('552'),
            })

            line_45 = self.env['bilan.passive.ligne'].search([('name','=','TOTAL GENERAL (I+II+III)'),('bilan_id','=',rec.id)])
            line_45.write({
            'net': line_44.net + line_39.net + line_26.net,
            'prev_net': line_44.prev_net + line_39.prev_net + line_26.prev_net,
            })

class BilanPassiveLignes(models.Model):
    _name = "bilan.passive.ligne"

    name = fields.Char(string=u"Nom",required=True,readonly=True)
    net  = fields.Float(string=u"Net",readonly=True)
    prev_net  = fields.Float(string=u"Net d'exercice précédent",readonly=True)
    
    # Code edis
    code_edi_net  = fields.Integer(string=u"Edi Net",readonly=True)
    code_edi_prev_net  = fields.Integer(string=u"E di Prev Net",readonly=True)
    
    # Relational fields
    bilan_id = fields.Many2one(string='bilan id', comodel_name='bilan.passive')
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('bilan.passive.ligne'))



