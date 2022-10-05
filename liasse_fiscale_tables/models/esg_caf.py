# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)

class ECGCAF(models.Model):
    _name = "esg.caf"

    _description = 'TABLEAU de ESG TFR'

    name = fields.Char(string=u"Nom",default="ESG CAF",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False,store=True,)
    line_ids = fields.One2many(string='Lignes',comodel_name='esg.caf.ligne',inverse_name='parent_id' )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('esg.caf'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    @api.model
    def create(self, values):
        return super(ECGCAF,self).create({
            'line_ids' : self.env['esg.caf.ligne'].create([{'name':'1. Résultat net de l\'exercice','code_edi_net':1372,'code_edi_prev_net':1386,'parent_id':self.id,},
                                                                {'name':'Bénéfice +','code_edi_net':1373,'code_edi_prev_net':1387,'parent_id':self.id,},
                                                                {'name':'Perte -','code_edi_net':1374,'code_edi_prev_net':1388,'parent_id':self.id,},
                                                                {'name':'2. (+) Dotations d\'exploitation (1)','code_edi_net':1375,'code_edi_prev_net':1389,'parent_id':self.id,},
                                                                {'name':'3. (+) Dotations financières (1)','code_edi_net':1376,'code_edi_prev_net':1390,'parent_id':self.id,},
                                                                {'name':'4. (+) Dotations non courantes (1)','code_edi_net':1377,'code_edi_prev_net':1391,'parent_id':self.id,},
                                                                {'name':'5. (-) Reprises d\'exploitation (2)','code_edi_net':1378,'code_edi_prev_net':1392,'parent_id':self.id,},
                                                                {'name':'6. (-) Reprises financières (2)','code_edi_net':1379,'code_edi_prev_net':1393,'parent_id':self.id,},
                                                                {'name':'7. (-) Reprises non courantes (2)(3)','code_edi_net':1380,'code_edi_prev_net':1394,'parent_id':self.id,},
                                                                {'name':'8. (-) Produits des cessions d\'immobilisations (1)','code_edi_net':1381,'code_edi_prev_net':1395,'parent_id':self.id,},
                                                                {'name':'9. (+) Valeurs nettes d\'amortiss. des immo. Cédées','code_edi_net':1382,'code_edi_prev_net':1396,'parent_id':self.id,},
                                                                {'name':'I. CAPACITE D\'AUTOFINANCEMENT (C.A.F.)','code_edi_net':1383,'code_edi_prev_net':1397,'parent_id':self.id,},
                                                                {'name':'10. (-) Distributions de bénéfices','code_edi_net':1384,'code_edi_prev_net':1398,'parent_id':self.id,},
                                                                {'name':'II. AUTOFINANCEMENT','code_edi_net':1385,'code_edi_prev_net':1399,'parent_id':self.id},
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
            line_1 = self.env['esg.caf.ligne'].search([('name','=','1. Résultat net de l\'exercice'),('parent_id','=',rec.id)])
            line_1.write({
            'net':self.bal_calulator_current_year(['71','73','75']) - self.bal_calulator_current_year(['61','63','65','67']),
            'prev_net':self.bal_calulator_previous_years(['71','73','75']) - self.bal_calulator_previous_years(['61','63','65','67']),
            })
            line_2 = self.env['esg.caf.ligne'].search([('name','=','Bénéfice +'),('parent_id','=',rec.id)])
            line_2.write({
            'net':abs(self.bal_calulator_current_year(['71','73','75']) - self.bal_calulator_current_year(['61','63','65','67'])) if line_1.net > 0 else 0 ,
            'prev_net':abs(self.bal_calulator_previous_years(['71','73','75']) - self.bal_calulator_previous_years(['61','63','65','67'])) if line_1.prev_net > 0 else 0,
            })
            line_3 = self.env['esg.caf.ligne'].search([('name','=','Perte -'),('parent_id','=',rec.id)])
            line_3.write({
            'net':self.bal_calulator_current_year(['61','63','65','67']) - self.bal_calulator_current_year(['71','73','75']) if  line_1.net < 0 else 0 ,
            'prev_net': self.bal_calulator_previous_years(['61','63','65','67']) - self.bal_calulator_previous_years(['71','73','75']) if line_1.prev_net < 0 else 0,
            })
            line_4 = self.env['esg.caf.ligne'].search([('name','=','2. (+) Dotations d\'exploitation (1)'),('parent_id','=',rec.id)])
            line_4.write({
            'net':self.bal_calulator_current_year(['619']),
            'prev_net':self.bal_calulator_previous_years(['619']),
            })
            line_5 = self.env['esg.caf.ligne'].search([('name','=','3. (+) Dotations financières (1)'),('parent_id','=',rec.id)])
            line_5.write({
            'net':self.bal_calulator_current_year(['639']),
            'prev_net':self.bal_calulator_previous_years(['639']),
            })
            line_6 = self.env['esg.caf.ligne'].search([('name','=','4. (+) Dotations non courantes (1)'),('parent_id','=',rec.id)])
            line_6.write({
            'net':self.bal_calulator_current_year(['659']),
            'prev_net':self.bal_calulator_previous_years(['659']),
            })
            line_7 = self.env['esg.caf.ligne'].search([('name','=','5. (-) Reprises d\'exploitation (2)'),('parent_id','=',rec.id)])
            line_7.write({
            'net':self.bal_calulator_current_year(['719'])  if self.bal_calulator_current_year(['719']) < 0  else - self.bal_calulator_current_year(['719']),
            'prev_net':self.bal_calulator_previous_years(['719']) if self.bal_calulator_previous_years(['719']) < 0 else - self.bal_calulator_previous_years(['719']),
            })
            line_8 = self.env['esg.caf.ligne'].search([('name','=','6. (-) Reprises financières (2)'),('parent_id','=',rec.id)])
            line_8.write({
            'net':self.bal_calulator_current_year(['739'])  if self.bal_calulator_current_year(['739']) < 0  else - self.bal_calulator_current_year(['739']),
            'prev_net':self.bal_calulator_previous_years(['739']) if self.bal_calulator_previous_years(['739']) < 0 else - self.bal_calulator_previous_years(['739']),
            })
            line_9 = self.env['esg.caf.ligne'].search([('name','=','7. (-) Reprises non courantes (2)(3)'),('parent_id','=',rec.id)])
            line_9.write({
            'net':self.bal_calulator_current_year(['759'])  if self.bal_calulator_current_year(['759']) < 0  else - self.bal_calulator_current_year(['759']),
            'prev_net':self.bal_calulator_previous_years(['759']) if self.bal_calulator_previous_years(['759']) < 0 else - self.bal_calulator_previous_years(['759']),
            })
            line_10 = self.env['esg.caf.ligne'].search([('name','=','8. (-) Produits des cessions d\'immobilisations (1)'),('parent_id','=',rec.id)])
            line_10.write({
            'net':self.bal_calulator_current_year(['751'])  if self.bal_calulator_current_year(['751']) < 0  else - self.bal_calulator_current_year(['751']),
            'prev_net':self.bal_calulator_previous_years(['751']) if self.bal_calulator_previous_years(['751']) < 0 else - self.bal_calulator_previous_years(['751']),
            })
            line_11 = self.env['esg.caf.ligne'].search([('name','=','9. (+) Valeurs nettes d\'amortiss. des immo. Cédées'),('parent_id','=',rec.id)])
            line_11.write({
            'net':abs(self.bal_calulator_current_year(['651'])),
            'prev_net':abs(self.bal_calulator_previous_years(['651'])),
            })

            line_12 = self.env['esg.caf.ligne'].search([('name','=','I. CAPACITE D\'AUTOFINANCEMENT (C.A.F.)'),('parent_id','=',rec.id)])
            line_12.write({
            'net':self.bal_calulator_current_year(['71','73','75','639','619','659','651']) - self.bal_calulator_current_year(['61','63','65','67','719','739','759','751']),
            'prev_net':self.bal_calulator_previous_years(['71','73','75','639','619','659','651']) - self.bal_calulator_previous_years(['61','63','65','67','719','739','759','751']),
            })
            line_13 = self.env['esg.caf.ligne'].search([('name','=','10. (-) Distributions de bénéfices'),('parent_id','=',rec.id)])
            line_13.write({
            'net':self.bal_calulator_current_year(['4465']),
            'prev_net':self.bal_calulator_previous_years(['4465']),
            })

            line_14 = self.env['esg.caf.ligne'].search([('name','=','II. AUTOFINANCEMENT'),('parent_id','=',rec.id)])
            line_14.write({
            'net':self.bal_calulator_current_year(['71','73','75','639','619','659','651']) - self.bal_calulator_current_year(['739','759','751','719','4465','65','63','61','67']),
            'prev_net':self.bal_calulator_previous_years(['71','73','75','619','639','659','651']) - self.bal_calulator_previous_years(['739','759','719','4465','751','65','63','61','67']),
            })
    
    def get_xml(self,parent):
        for rec in self:
            if rec.line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(8)
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                esg_tfr = self.env['esg.tfr'].search([('fy_n_id','=',rec.fy_n_id.id),('company_id','=',self.env.company.id)])
                if esg_tfr:
                    for line in esg_tfr.line_ids:
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
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_net)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.net)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_prev_net)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.prev_net)
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
                
            else:
                pass
            
class ESGTFRLignes(models.Model):
    _name = "esg.caf.ligne"

    name = fields.Char(string=u"Nom",required=True,readonly=True)
    net  = fields.Float(string=u"Net",readonly=True)
    prev_net  = fields.Float(string=u"Net d'exercice précédent",readonly=True)
    
    # Code edi Fields
    code_edi_net  = fields.Integer(string=u"Edi Net",readonly=True)
    code_edi_prev_net  = fields.Integer(string=u"Edi Net précédent",readonly=True)
    
    # Relational Fields 
    parent_id = fields.Many2one(string='Parent Id', comodel_name='esg.caf')
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('esg.caf.ligne'))



