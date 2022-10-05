# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile

import os
directory = os.path.dirname(__file__)

class AffectationResultatsIntervenue(models.Model):
    _name = 'affectation.resultats.intervenue'
    _description = 'AFFECTATION DES RESULTATS INTERVENUE'

    name = fields.Char(string=u"Nom",default="ETAT D'AFFECTATION DES RESULTATS INTERVENUE AU COURS DE L'EXERCICE",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False,store=True,)
    affectation_resultats_intervenue_line1_ids = fields.One2many(comodel_name="affectation.resultats.intervenue.line1", inverse_name="affectation_resultats_intervenue_id", string="ORIGINE DES RESULTATS A AFFECTER", required=False, copy=True )
    affectation_resultats_intervenue_line2_ids = fields.One2many(comodel_name="affectation.resultats.intervenue.line2", inverse_name="affectation_resultats_intervenue_id", string="AFFECTATION DES RESULTATS", required=False, copy=True )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('affectation.resultats.intervenue'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    

    @api.model
    def create(self, values):
        return super(AffectationResultatsIntervenue,self).create({
            'fy_n_id':self.fy_n_id.id,
            'affectation_resultats_intervenue_line1_ids' : self.env['affectation.resultats.intervenue.line1'].create([{'name':'Décision du (Date AGOA ....)','code':'000000','affectation_resultats_intervenue_id':self.id,},
                                                                  {'name':'Report à nouveau (Antérieur) + ou(-)','code_edi_montant':471,'code':'116','affectation_resultats_intervenue_id':self.id,},
                                                                  {'name':'Résultat net en instance d\'affectation + ou(-)','code_edi_montant':473,'code':'118','affectation_resultats_intervenue_id':self.id,},
                                                                  {'name':'Résultat net de l\'exercice + ou(-)','code_edi_montant':475,'code':'119','affectation_resultats_intervenue_id':self.id,},
                                                                  {'name':'Prélèvement sur les réserves +','code_edi_montant':477,'code':'115','affectation_resultats_intervenue_id':self.id,},
                                                                  {'name':'Autres prélèvements +','code_edi_montant':479,'code':'','affectation_resultats_intervenue_id':self.id,},
                                                                  {'name':'Total A','code':'','code_edi_montant':481,'affectation_resultats_intervenue_id':self.id,}
                                                                  ]),
            'affectation_resultats_intervenue_line2_ids' : self.env['affectation.resultats.intervenue.line2'].create([{'name':'Réserve Légale','code_edi_montant':483,'code':'1140','affectation_resultats_intervenue_id':self.id,},
                                                                  {'name':'Autres réserves','code':'115','code_edi_montant':485,'affectation_resultats_intervenue_id':self.id,},
                                                                  {'name':'Tantièmes (Abrogé)','code':'4465','code_edi_montant':487,'affectation_resultats_intervenue_id':self.id,},
                                                                  {'name':'Dividendes (Mt Brut)(1)','code_edi_montant':489,'code':'4465','affectation_resultats_intervenue_id':self.id,},
                                                                  {'name':'Autres affectation','code_edi_montant':491,'code':'','affectation_resultats_intervenue_id':self.id,},
                                                                  {'name':'Report à nouveau reportable','code_edi_montant':493,'code':'116','affectation_resultats_intervenue_id':self.id,},
                                                                  {'name':'Total B','code':'116','code_edi_montant':495,'affectation_resultats_intervenue_id':self.id,}
                                                                  ]),
        })

    def from_string_to_list(self,val,list):
        list = []
        for x in str(val):
            list.append(x)
        return list
    
    def list_verification(self,list1,list2):
        if len(list1) == 2:
            if list1[0] == list2[0] and list1[1] == list2[1] :
                return True
        if len(list1) == 3:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2] :
                return True
        elif len(list1) == 4:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2] and list1[3] == list2[3] :
                return True
        elif len(list1) == 5:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2] and list1[3] == list2[3] and list1[4] == list2[4]:
                return True
        elif len(list1) == 6:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2] and list1[3] == list2[3] and list1[4] == list2[4] and list1[5] == list2[5]:
                return True
        elif len(list1) == 7:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2] and list1[3] == list2[3] and list1[4] == list2[4] and list1[5] == list2[5] and list1[6] == list2[6] :
                return True
        elif len(list1) == 8:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2] and list1[3] == list2[3] and list1[4] == list2[4] and list1[5] == list2[5] and list1[6] == list2[6] and list1[7] == list2[7] :
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

    def debit_calulator_current_year(self,codes):
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
                                        bal +=  item.debit                                       
            return bal
    
    def credit_calulator_current_year(self,codes):
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
                                        bal +=  item.credit                                       
            return bal
            
    def get_lines(self):
        for rec in self:
            line_1 = self.env['affectation.resultats.intervenue.line1'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Report à nouveau (Antérieur) + ou(-)')])
            line_1.write({
                'montant':  self.bal_calulator_previous_years(['1161']) if self.bal_calulator_previous_years(['1161']) != 0 else self.bal_calulator_previous_years(['1169']) ,
            })
            line_2 = self.env['affectation.resultats.intervenue.line1'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Résultat net en instance d\'affectation + ou(-)')])
            line_2.write({
                'montant':  0 ,
            })
            line_3 = self.env['affectation.resultats.intervenue.line1'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Résultat net de l\'exercice + ou(-)')])
            line_3.write({
                'montant':self.bal_calulator_previous_years(['71','73','75']) - self.bal_calulator_previous_years(['61','63','65','67']),
            })
            line_4 =self.env['affectation.resultats.intervenue.line1'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Prélèvement sur les réserves +')])
            line_4.write({
                'montant':self.bal_calulator_previous_years(['1140']) ,
            })
            
            line_6 = self.env['affectation.resultats.intervenue.line1'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Autres prélèvements +')])
            line_6.write({
                'montant':self.bal_calulator_previous_years(['115']) ,
                })
            line_7 = self.env['affectation.resultats.intervenue.line1'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Total A')])
            line_7.write({
                'montant': line_1.montant + line_2.montant + line_3.montant + line_4.montant + line_6.montant,
            })
            # ______________
            line_11 = self.env['affectation.resultats.intervenue.line2'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Réserve Légale')])
            line_11.write({
                'montant':  self.bal_calulator_current_year(['1140']) ,
            })
            line_21 = self.env['affectation.resultats.intervenue.line2'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Autres réserves')])
            line_21.write({
                'montant':  self.bal_calulator_current_year(['115']) ,
            })
            line_31 = self.env['affectation.resultats.intervenue.line2'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Tantièmes (Abrogé)')])
            line_31.write({
                'montant':  0 ,
            })
            line_41 =self.env['affectation.resultats.intervenue.line2'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Dividendes (Mt Brut)(1)')])
            line_41.write({
                'montant':  self.debit_calulator_current_year(['4465']) ,
            })
            line_61 = self.env['affectation.resultats.intervenue.line2'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Autres affectation')])
            line_61.write({
                 'montant':  self.credit_calulator_current_year(['44570001']) ,
                })
            line_71 = self.env['affectation.resultats.intervenue.line2'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Report à nouveau reportable')])
            line_71.write({
                'montant':  self.bal_calulator_current_year(['1161']) if self.bal_calulator_current_year(['1161']) != 0 else self.bal_calulator_current_year(['1169']) ,

            })
            line_81 = self.env['affectation.resultats.intervenue.line2'].search([('affectation_resultats_intervenue_id','=',rec.id),('name','=','Total B')])
            line_81.write({
                'montant': line_11.montant + line_21.montant + line_31.montant + line_41.montant + line_61.montant + line_71.montant  ,
            })   
    
    def get_xml(self,parent):
        for rec in self:
            if rec.affectation_resultats_intervenue_line1_ids and rec.affectation_resultats_intervenue_line2_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(5) # read documentation XML
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                for line in rec.affectation_resultats_intervenue_line1_ids:
                    if line.code != '000000':
                        valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                        cellule = etree.SubElement(valeur_cellule, "cellule")
                        etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_montant)
                        etree.SubElement(valeur_cellule, "valeur").text = str(line.montant)
                for line in rec.affectation_resultats_intervenue_line2_ids:
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.code_edi_montant)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant)
                    
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")

            else:
                pass
                    
class AffectationResultatsIntervenueLine1(models.Model):
    _name = 'affectation.resultats.intervenue.line1'
    _description = 'LIGNES AFFECTATION DES RESULTATS INTERVENUE 1'

    name = fields.Char(string=u"Nom",required=True,store=True)
    code = fields.Char(string=u"Code", required=False, )
    montant = fields.Float(string=u"Montant",  required=False, )
    
    # Code Edi 
    code_edi_montant = fields.Integer(string=u"Montant",  required=False,readonly=True )
    
    # Relational Fields
    affectation_resultats_intervenue_id = fields.Many2one(comodel_name="affectation.resultats.intervenue", string="AFFECTATION DES RESULTATS INTERVENUE", required=False, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('affectation.resultats.intervenue.line1'))

class AffectationResultatsIntervenueLine2(models.Model):
    _name = 'affectation.resultats.intervenue.line2'
    _description = 'LIGNES AFFECTATION DES RESULTATS INTERVENUE 2'

    name = fields.Char(string=u"Nom",required=True,readonly=True,store=True)
    code = fields.Char(string=u"Code", required=False,store=True )
    montant = fields.Float(string=u"Montant",  required=False, )
    
    # Code Edi 
    code_edi_montant = fields.Integer(string=u"Montant",  required=False,readonly=True )
    
    # Relational Fields
    affectation_resultats_intervenue_id = fields.Many2one(comodel_name="affectation.resultats.intervenue", string="AFFECTATION DES RESULTATS INTERVENUE", required=False, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('affectation.resultats.intervenue.line2'))