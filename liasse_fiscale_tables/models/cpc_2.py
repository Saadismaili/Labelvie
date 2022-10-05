# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile

import os
directory = os.path.dirname(__file__)

class CHARGELOSS(models.Model):
    _name = "charge.loss"

    _description = 'TABLEAU de LOSS'

    name = fields.Char(string=u"Nom",default="Account Report Profit and Loss",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False,store=True,)
    line_ids = fields.One2many(string='Lignes',comodel_name='charge.loss.ligne',inverse_name='parent_id' )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('charge.loss'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    @api.model
    def create(self, values):
        return super(CHARGELOSS,self).create({
            'line_ids' : self.env['charge.loss.ligne'].create([{'name':'RESULTAT COURANT (reports)','parent_id':self.id,},
                                                                {'name':'VIII. PRODUITS NON COURANTS','code_edi_current':11391 , 'code_edi_previous':11392 , 'code_edi_net': 11393, 'code_edi_prev_net':11394,'parent_id':self.id,},
                                                                {'name':'* Produits des cessions d\'immobilisations','code_edi_current':11341 , 'code_edi_previous':11342 , 'code_edi_net': 11343, 'code_edi_prev_net':11344,'parent_id':self.id,},
                                                                {'name':'* Subventions d\'équilibre','code_edi_current':11346 , 'code_edi_previous':11347 , 'code_edi_net': 11348, 'code_edi_prev_net':11349,'parent_id':self.id,},
                                                                {'name':'* Reprises sur subventions d\'investissement','code_edi_current':11351 , 'code_edi_previous':11352 , 'code_edi_net': 11353, 'code_edi_prev_net':11354,'parent_id':self.id,},
                                                                {'name':'* Autres produits non courants','code_edi_current':11356 , 'code_edi_previous':11357 , 'code_edi_net': 11358, 'code_edi_prev_net':11359,'parent_id':self.id,},
                                                                {'name':'* Reprises non courantes ; transferts de charges','code_edi_current':11361 , 'code_edi_previous':11362 , 'code_edi_net': 11363, 'code_edi_prev_net':11364,'parent_id':self.id,},
                                                                {'name':'Total VIII','code_edi_current':11366 , 'code_edi_previous':11367 , 'code_edi_net': 11368, 'code_edi_prev_net':11369,'parent_id':self.id,},
                                                                {'name':'IX. CHARGES NON COURANTES','code_edi_current':11396 , 'code_edi_previous':11397 , 'code_edi_net': 11398, 'code_edi_prev_net':11399,'parent_id':self.id,},
                                                                {'name':'* Valeurs nettes d\'amortissements des immobilisations cédées','code_edi_current':11371 , 'code_edi_previous':11372 , 'code_edi_net': 11373, 'code_edi_prev_net':11374,'parent_id':self.id,},
                                                                {'name':'* Subventions accordées','code_edi_current':11376 , 'code_edi_previous':11377 , 'code_edi_net': 11378, 'code_edi_prev_net':11379,'parent_id':self.id,},
                                                                {'name':'* Autres charges non courantes','code_edi_current':11381 , 'code_edi_previous':11382 , 'code_edi_net': 11383, 'code_edi_prev_net':11384,'parent_id':self.id,},
                                                                {'name':'* Dotations non courantes aux amortissements et aux provisions','code_edi_current':11386 , 'code_edi_previous':11387 , 'code_edi_net': 11388, 'code_edi_prev_net':11389,'parent_id':self.id,},
                                                                {'name':'Total IX','code_edi_current':11406 , 'code_edi_previous':11407 , 'code_edi_net': 11408, 'code_edi_prev_net':11409,'parent_id':self.id,},
                                                                {'name':'X. RESULTAT NON COURANT (VIII-IX)','code_edi_current':11401 , 'code_edi_previous':11402 , 'code_edi_net': 11403, 'code_edi_prev_net':11404,'parent_id':self.id,},
                                                                {'name':'XI. RESULTAT AVANT IMPOTS (VII+X)','code_edi_current':11411 , 'code_edi_previous':11412 , 'code_edi_net': 11413, 'code_edi_prev_net':11414,'parent_id':self.id,},
                                                                {'name':'XII. IMPOTS SUR LES RESULTATS','code_edi_current':11416 , 'code_edi_previous':11417 , 'code_edi_net': 11418, 'code_edi_prev_net':11419,'parent_id':self.id,},
                                                                {'name':'RESULTAT NET (XI-XII)','code_edi_current':11421 , 'code_edi_previous':11422 , 'code_edi_net': 11423, 'code_edi_prev_net':11424,'parent_id':self.id,},
                                                                {'name':'XIV. TOTAL DES PRODUITS (I+IV+VIII)','code_edi_current':11426 , 'code_edi_previous':11427 , 'code_edi_net': 11428, 'code_edi_prev_net':11429,'parent_id':self.id,},
                                                                {'name':'XV. TOTAL DES CHARGES (II+V+IX+XII)','code_edi_current':11431 , 'code_edi_previous':11432 , 'code_edi_net': 11433, 'code_edi_prev_net':11434,'parent_id':self.id,},
                                                                {'name':'RESULTAT NET (total des produits-total des charges) ','code_edi_current':11436 , 'code_edi_previous':11437 , 'code_edi_net': 11438, 'code_edi_prev_net':11439,'parent_id':self.id,},
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
    # this function returns the Net current year balance amount of each specific code assigned
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
    # this function returns the Net previous year balance amount of each specific code assigned
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
            
            line_2 = self.env['charge.loss.ligne'].search([('name','=','* Produits des cessions d\'immobilisations'),('parent_id','=',rec.id)])
            line_2.write({
            'current':self.bal_calulator_current_year(['751']) - self.bal_calulator_current_year(['7518']) ,
            'previous':self.bal_calulator_current_year(['7518']) ,
            'net':self.bal_calulator_current_year(['751']) ,
            'prev_net':self.bal_calulator_previous_years(['751']),
            })
            line_3 = self.env['charge.loss.ligne'].search([('name','=','* Subventions d\'équilibre'),('parent_id','=',rec.id)])
            line_3.write({
            'current':self.bal_calulator_current_year(['756']) - self.bal_calulator_current_year(['7568']) ,
            'previous':self.bal_calulator_current_year(['7568']) ,
            'net':self.bal_calulator_current_year(['756']),
            'prev_net':self.bal_calulator_previous_years(['756']) ,
            })
            line_4 = self.env['charge.loss.ligne'].search([('name','=','* Reprises sur subventions d\'investissement'),('parent_id','=',rec.id)])
            line_4.write({
            'current':self.bal_calulator_current_year(['757'])  - self.bal_calulator_current_year(['7578']),
            'previous':self.bal_calulator_current_year(['7578']) ,
            'net':self.bal_calulator_current_year(['757']) ,
            'prev_net':self.bal_calulator_previous_years(['757'])  ,
            })
            line_5 = self.env['charge.loss.ligne'].search([('name','=','* Autres produits non courants'),('parent_id','=',rec.id)])
            line_5.write({
            'current':self.bal_calulator_current_year(['758']) - self.bal_calulator_current_year(['7588']) ,
            'previous':self.bal_calulator_current_year(['7588']) ,
            'net':self.bal_calulator_current_year(['758']) ,
            'prev_net':self.bal_calulator_previous_years(['758']),
            })
            line_6 = self.env['charge.loss.ligne'].search([('name','=','* Reprises non courantes  ; transferts  de charges'),('parent_id','=',rec.id)])
            line_6.write({
            'current':self.bal_calulator_current_year(['759']) - self.bal_calulator_current_year(['7598']) ,
            'previous':self.bal_calulator_current_year(['7598']) ,
            'net':self.bal_calulator_current_year(['759']) ,
            'prev_net':self.bal_calulator_previous_years(['759']),
            })
            line_7 = self.env['charge.loss.ligne'].search([('name','=','VIII. PRODUITS NON COURANTS'),('parent_id','=',rec.id)])
            line_7.write({
            'current':self.bal_calulator_current_year(['751','759','758','757','756']) - self.bal_calulator_current_year(['7518','7598','7588','7578','7568']) ,
            'previous':self.bal_calulator_current_year(['7518','7598','7588','7578','7568']) ,
            'net':self.bal_calulator_current_year(['751','759','758','757','756']) ,
            'prev_net':self.bal_calulator_previous_years(['751','759','758','757','756']),
            })


            line_8 = self.env['charge.loss.ligne'].search([('name','=','* Valeurs nettes d\'amortissements des immobilisations cédées'),('parent_id','=',rec.id)])
            line_8.write({
            'current':self.bal_calulator_current_year(['651']) - self.bal_calulator_current_year(['6518']),
            'previous':self.bal_calulator_current_year(['6518']) ,
            'net':self.bal_calulator_current_year(['651']) ,
            'prev_net':self.bal_calulator_previous_years(['651']) ,
            })
            line_9 = self.env['charge.loss.ligne'].search([('name','=','* Subventions accordées'),('parent_id','=',rec.id)])
            line_9.write({
            'current':self.bal_calulator_current_year(['656']) - self.bal_calulator_current_year(['6568']),
            'previous':self.bal_calulator_current_year(['6568']) ,
            'net':self.bal_calulator_current_year(['656']) ,
            'prev_net':self.bal_calulator_previous_years(['656']),
            })
            line_10 = self.env['charge.loss.ligne'].search([('name','=','* Autres charges non courantes'),('parent_id','=',rec.id)])
            line_10.write({
            'current':self.bal_calulator_current_year(['658']) - self.bal_calulator_current_year(['6588']),
            'previous':self.bal_calulator_current_year(['6588']) ,
            'net':self.bal_calulator_current_year(['658']),
            'prev_net':self.bal_calulator_previous_years(['658']),
            })
            line_11 = self.env['charge.loss.ligne'].search([('name','=','* Dotations non courantes aux amortissements et aux provisions'),('parent_id','=',rec.id)])
            line_11.write({
           'current':self.bal_calulator_current_year(['659']) - self.bal_calulator_current_year(['6598']),
            'previous':self.bal_calulator_current_year(['6598']) ,
            'net':self.bal_calulator_current_year(['659']),
            'prev_net':self.bal_calulator_previous_years(['659']),
            })
            line_12 = self.env['charge.loss.ligne'].search([('name','=','IX. CHARGES NON COURANTES'),('parent_id','=',rec.id)])
            line_12.write({
           'current':self.bal_calulator_current_year(['651','656','658','659']) - self.bal_calulator_current_year(['6518','6568','6588','6598']),
            'previous':self.bal_calulator_current_year(['6518','6568','6588','6598']) ,
            'net':self.bal_calulator_current_year(['651','656','658','659']),
            'prev_net':self.bal_calulator_previous_years(['651','656','658','659']),
            })
            
            line_13 = self.env['charge.loss.ligne'].search([('name','=','Total VIII'),('parent_id','=',rec.id)])
            line_13.write({
            'current':self.bal_calulator_current_year(['751','759','758','757','756']) - self.bal_calulator_current_year(['7518','7598','7588','7578','7568']) ,
            'previous':self.bal_calulator_current_year(['7518','7598','7588','7578','7568']) ,
            'net':self.bal_calulator_current_year(['751','759','758','757','756']),
            'prev_net':self.bal_calulator_previous_years(['751','759','758','757','756']),
            })

            line_14 = self.env['charge.loss.ligne'].search([('name','=','Total IX'),('parent_id','=',rec.id)])
            line_14.write({
            'current':self.bal_calulator_current_year(['651','656','658','659']) - self.bal_calulator_current_year(['6518','6568','6588','6598']),
            'previous':self.bal_calulator_current_year(['6518','6568','6588','6598']) ,
            'net':self.bal_calulator_current_year(['651','656','658','659']),
            'prev_net':self.bal_calulator_previous_years(['651','656','658','659']),
            })

            line_15 = self.env['charge.loss.ligne'].search([('name','=','X. RESULTAT NON COURANT (VIII-IX)'),('parent_id','=',rec.id)])
            line_15.write({
            'current':self.bal_calulator_current_year(['751','759','758','757','756','6518','6568','6588','6598']) - self.bal_calulator_current_year(['651','656','658','659','7518','7598','7588','7578','7568']) ,
            'previous':self.bal_calulator_current_year(['7518','7598','7588','7578','7568']) - self.bal_calulator_current_year(['6518','6568','6588','6598']) ,
            'net':self.bal_calulator_current_year(['751','759','758','757','756']),
            'prev_net':self.bal_calulator_previous_years(['751','759','758','757','756']),
            })
            line_x = self.env['charge.profit.ligne'].search([('name','=',"VII. RESULTAT COURANT (III+VI)"),('parent_id.fy_n_id','=',rec.fy_n_id.id)])

            line_1 = self.env['charge.loss.ligne'].search([('name','=','RESULTAT COURANT (reports)'),('parent_id','=',rec.id)])
            line_1.write({
            'current':  line_x.current ,
            'previous': line_x.previous ,
            'net':  line_x.net ,
            'prev_net':  line_x.prev_net,
            })

            line_16 = self.env['charge.loss.ligne'].search([('name','=','XI. RESULTAT AVANT IMPOTS (VII+X)'),('parent_id','=',rec.id)])
            line_16.write({
            'current': line_15.current + line_x.current ,
            'previous':line_15.previous + line_x.previous ,
            'net': line_16.current + line_16.previous ,
            'prev_net': line_15.prev_net + line_x.prev_net,
            })

            line_17 = self.env['charge.loss.ligne'].search([('name','=','XII. IMPOTS SUR LES RESULTATS'),('parent_id','=',rec.id)])
            line_17.write(
            {
            'current':self.bal_calulator_current_year(['67']),
            'previous':0 ,
            'net':self.bal_calulator_current_year(['67']),
            'prev_net':self.bal_calulator_previous_years(['67']),
            })

            line_18 = self.env['charge.loss.ligne'].search([('name','=','RESULTAT NET (XI-XII)'),('parent_id','=',rec.id)])
            line_18.write({
            'current':line_16.current - line_17.current ,
            'previous':line_16.previous - line_17.previous ,
            'net':line_16.net - line_17.net ,
            'prev_net':line_16.prev_net - line_17.prev_net,
            })

            line_19 = self.env['charge.loss.ligne'].search([('name','=','XIV. TOTAL DES PRODUITS (I+IV+VIII)'),('parent_id','=',rec.id)])
            line_19.write({
            'current':self.bal_calulator_current_year(['71','73','75']) - self.bal_calulator_current_year(['7118','7128','7148','7168','7188','7198','7328','7338','7388','7398','7518','7568','7578','7588','7598']),
            'previous':self.bal_calulator_current_year(['7118','7128','7148','7168','7188','7198','7328','7338','7388','7398','7518','7568','7578','7588','7598']) ,
            'net':self.bal_calulator_current_year(['71','73','75']) ,
            'prev_net':self.bal_calulator_previous_years(['71','73','75']) ,
            })
            line_II = self.env['charge.profit.ligne'].search([('name','=',"Total II"),('parent_id.fy_n_id','=',rec.fy_n_id.id)])
            line_V = self.env['charge.profit.ligne'].search([('name','=',"Total V"),('parent_id.fy_n_id','=',rec.fy_n_id.id)])
            line_20 = self.env['charge.loss.ligne'].search([('name','=','XV. TOTAL DES CHARGES (II+V+IX+XII)'),('parent_id','=',rec.id)])
            line_20.write({
            'current':line_14.current + line_17.current + line_II.current +line_V.current ,
            'previous':line_14.previous + line_17.previous +line_II.previous +line_V.previous ,
            'net':line_14.net +line_17.net + line_V.net +line_II.net,
            'prev_net':line_14.prev_net + line_17.prev_net + line_II.prev_net +line_V.prev_net,
            })
            line_21 = self.env['charge.loss.ligne'].search([('name','=','RESULTAT NET (total des produits-total des charges) '),('parent_id','=',rec.id)])
            line_21.write({
            'current':line_19.current - line_20.current ,
            'previous':line_19.previous - line_20.previous ,
            'net':line_19.net - line_20.net ,
            'prev_net':line_19.prev_net - line_20.prev_net,
            })
    
    def get_xml(self,parent):
        for rec in self:
            if rec.line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(6)
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                cpc_1 = self.env['charge.profit'].search([('fy_n_id','=',rec.fy_n_id.id),('company_id','=',self.env.company.id)])
                if cpc_1:
                    for line in cpc_1.line_ids:
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_current)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.current)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_previous)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.previous)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_net)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.net)
                        
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_prev_net)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.prev_net)
                for line in rec.line_ids:
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_current)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.current)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_previous)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.previous)
                    
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

class CHARGELOSSLignes(models.Model):
    _name = "charge.loss.ligne"

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
    
    # Relational fields
    parent_id = fields.Many2one(string='Parent Id', comodel_name='charge.loss')
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('charge.loss.ligne'))



