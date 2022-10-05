# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)

class ECGTFR(models.Model):
    _name = "esg.tfr"

    _description = 'TABLEAU de ESG TFR'

    name = fields.Char(string=u"Nom",default="ESG TFR",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False,store=True,)
    line_ids = fields.One2many(string='Lignes',comodel_name='esg.tfr.ligne',inverse_name='parent_id' )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('esg.tfr'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    @api.model
    def create(self, values):
        return super(ECGTFR,self).create({
            'line_ids' : self.env['esg.tfr.ligne'].create([{'name':'1. Ventes de Marchandises ( en l\'état)','code_edi_net':1308,'code_edi_prev_net':1333,'parent_id':self.id,},
                                                            {'name':'2. (-) Achats revendus de marchandises','code_edi_net':1309,'code_edi_prev_net':1334,'parent_id':self.id,},
                                                            {'name':'I. (=) MARGE BRUTE SUR VENTES EN L\'ETAT','code_edi_net':1310,'code_edi_prev_net':1335,'parent_id':self.id,},
                                                            {'name':'II. (+) PRODUCTION DE L\'EXERCICE (3+4+5)','code_edi_net':1311,'code_edi_prev_net':1336,'parent_id':self.id,},
                                                            {'name':'3. Ventes de biens et services produits','code_edi_net':1312,'code_edi_prev_net':1337,'parent_id':self.id,},
                                                            {'name':'4. Variation stocks produits','code_edi_net':1313,'code_edi_prev_net':1338,'parent_id':self.id,},
                                                            {'name':'5. Immobilisations produites par l\'entreprise pour elle-même','code_edi_net':1314,'code_edi_prev_net':1339,'parent_id':self.id,},
                                                            {'name':'III. (-) CONSOMMATION DE L\'EXERCICE (6+7)','code_edi_net':1315,'code_edi_prev_net':1340,'parent_id':self.id,},
                                                            {'name':'6. Achats consommés de matières et fournitures','code_edi_net':1316,'code_edi_prev_net':1341,'parent_id':self.id,},
                                                            {'name':'7. Autres charges externes','code_edi_net':1317,'code_edi_prev_net':1342,'parent_id':self.id,},
                                                            {'name':'IV. (=) VALEUR AJOUTEE (I+II+III)','code_edi_net':1318,'code_edi_prev_net':1343,'parent_id':self.id,},
                                                            {'name':'8. (+) Subventions d\'exploitation','code_edi_net':1319,'code_edi_prev_net':1344,'parent_id':self.id,},
                                                            {'name':'9. (-) Impôts et taxes','code_edi_net':1320,'code_edi_prev_net':1345,'parent_id':self.id,},
                                                            {'name':'10. (-) Charges de personnel','code_edi_net':1321,'code_edi_prev_net':1346,'parent_id':self.id,},
                                                            {'name':'V. (=) EXCEDENT BRUT D\'EXPLOITATION (EBE) OU INSUFFISANCE BRUTE D\'EXPLOITATION (IBE)','code_edi_net':4063,'code_edi_prev_net':4064,'parent_id':self.id,},
                                                            {'name':'11. (+) Autres produits d\'exploitation','code_edi_net':4066,'code_edi_prev_net':4067,'parent_id':self.id,},
                                                            {'name':'12. (-) Autres charges d\'exploitation','code_edi_net':1324,'code_edi_prev_net':1349,'parent_id':self.id,},
                                                            {'name':'13. (+) Reprises d\'exploitation, transferts de charges','code_edi_net':1325,'code_edi_prev_net':1350,'parent_id':self.id,},
                                                            {'name':'14. (-) Dotations d\'exploitation','code_edi_net':1326,'code_edi_prev_net':1351,'parent_id':self.id,},
                                                            {'name':'VI. (=) RESULTAT D\'EXPLOITATION (+ou-)','code_edi_net':1327,'code_edi_prev_net':1352,'parent_id':self.id,},
                                                            {'name':'VII. (+/-) RESULTAT FINANCIER','code_edi_net':1328,'code_edi_prev_net':1353,'parent_id':self.id,},
                                                            {'name':'VIII. (=) RESULTAT COURANT (+ou-)','code_edi_net':1329,'code_edi_prev_net':1354,'parent_id':self.id,},
                                                            {'name':'IX. (+/-) RESULTAT NON COURANT','code_edi_net':1330,'code_edi_prev_net':1355,'parent_id':self.id,},
                                                            {'name':'15. (-) IMPOTS SUR LES RESULTATS','code_edi_net':1331,'code_edi_prev_net':1356,'parent_id':self.id,},
                                                            {'name':'X. (=) RESULTAT NET DE L\'EXERCICE','code_edi_net':1332,'code_edi_prev_net':1357,'parent_id':self.id,},
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
            line_1 = self.env['esg.tfr.ligne'].search([('name','=','1. Ventes de Marchandises ( en l\'état)'),('parent_id','=',rec.id)])
            line_1.write({
            'net':self.bal_calulator_current_year(['711']),
            'prev_net':self.bal_calulator_previous_years(['711']),
            })
            line_2 = self.env['esg.tfr.ligne'].search([('name','=','2. (-) Achats revendus de marchandises'),('parent_id','=',rec.id)])
            line_2.write({
            'net':-abs(self.bal_calulator_current_year(['611'])),
            'prev_net':-abs(self.bal_calulator_previous_years(['611'])) ,
            })
            line_3 = self.env['esg.tfr.ligne'].search([('name','=','I. (=) MARGE BRUTE SUR VENTES EN L\'ETAT'),('parent_id','=',rec.id)])
            line_3.write({
            'net':self.bal_calulator_current_year(['711'])-self.bal_calulator_current_year(['611']),
            'prev_net':self.bal_calulator_previous_years(['711']) - self.bal_calulator_previous_years(['611']),
            })
            line_4 = self.env['esg.tfr.ligne'].search([('name','=','II. (+) PRODUCTION DE L\'EXERCICE (3+4+5)'),('parent_id','=',rec.id)])
            line_4.write({
            'net':abs(self.bal_calulator_current_year(['712','713','714'])),
            'prev_net':abs(self.bal_calulator_previous_years(['712','713','714'])),
            })
            line_5 = self.env['esg.tfr.ligne'].search([('name','=','3. Ventes de biens et services produits'),('parent_id','=',rec.id)])
            line_5.write({
            'net':self.bal_calulator_current_year(['712']),
            'prev_net':self.bal_calulator_previous_years(['712']),
            })
            line_6 = self.env['esg.tfr.ligne'].search([('name','=','4. Variation stocks produits'),('parent_id','=',rec.id)])
            line_6.write({
            'net':self.bal_calulator_current_year(['713']),
            'prev_net':self.bal_calulator_previous_years(['713']),
            })
            line_7 = self.env['esg.tfr.ligne'].search([('name','=','5. Immobilisations produites par l\'entreprise pour elle-même'),('parent_id','=',rec.id)])
            line_7.write({
            'net':self.bal_calulator_current_year(['714']),
            'prev_net':self.bal_calulator_previous_years(['714']),
            })
            line_8 = self.env['esg.tfr.ligne'].search([('name','=','III. (-) CONSOMMATION DE L\'EXERCICE (6+7)'),('parent_id','=',rec.id)])
            line_8.write({
            'net':self.bal_calulator_current_year(['612','613','614']),
            'prev_net':self.bal_calulator_previous_years(['612','613','614']),
            })
            line_9 = self.env['esg.tfr.ligne'].search([('name','=','6. Achats consommés de matières et fournitures'),('parent_id','=',rec.id)])
            line_9.write({
            'net':self.bal_calulator_current_year(['612']),
            'prev_net':self.bal_calulator_previous_years(['612']),
            })
            line_10 = self.env['esg.tfr.ligne'].search([('name','=','7. Autres charges externes'),('parent_id','=',rec.id)])
            line_10.write({
            'net':self.bal_calulator_current_year(['613','614']),
            'prev_net':self.bal_calulator_previous_years(['613','614']),
            })
            line_11 = self.env['esg.tfr.ligne'].search([('name','=','IV. (=) VALEUR AJOUTEE (I+II+III)'),('parent_id','=',rec.id)])
            line_11.write({
            'net':self.bal_calulator_current_year(['711','712','713','714']) - self.bal_calulator_current_year(['611','612','613','614']),
            'prev_net':self.bal_calulator_previous_years(['711','712','713','714']) - self.bal_calulator_previous_years(['611','612','613','614']),
            })
            line_12 = self.env['esg.tfr.ligne'].search([('name','=','8. (+) Subventions d\'exploitation'),('parent_id','=',rec.id)])
            line_12.write({
            'net':abs(self.bal_calulator_current_year(['716'])),
            'prev_net':abs(self.bal_calulator_previous_years(['716'])),
            })

            line_13 = self.env['esg.tfr.ligne'].search([('name','=','9. (-) Impôts et taxes'),('parent_id','=',rec.id)])
            line_13.write({
            'net':self.bal_calulator_current_year(['616']) if self.bal_calulator_current_year(['616']) <0 else - self.bal_calulator_current_year(['616']),
            'prev_net':self.bal_calulator_previous_years(['616']) if self.bal_calulator_previous_years(['616']) < 0 else - self.bal_calulator_previous_years(['616']),
            })

            line_14 = self.env['esg.tfr.ligne'].search([('name','=','10. (-) Charges de personnel'),('parent_id','=',rec.id)])
            line_14.write({
            'net':self.bal_calulator_current_year(['617'])if self.bal_calulator_current_year(['617']) <0 else -self.bal_calulator_current_year(['617']),
            'prev_net':self.bal_calulator_previous_years(['617']) if self.bal_calulator_previous_years(['617']) <0 else -self.bal_calulator_previous_years(['617']),
            })
            line_15 = self.env['esg.tfr.ligne'].search([('name','=','V. (=) EXCEDENT BRUT D\'EXPLOITATION (EBE) OU INSUFFISANCE BRUTE D\'EXPLOITATION (IBE)'),('parent_id','=',rec.id)])
            line_15.write({
            'net':self.bal_calulator_current_year(['711','712','713','714','716']) - self.bal_calulator_current_year(['611','612','613','614','616','617']),
            'prev_net':self.bal_calulator_previous_years(['711','712','713','714','716']) -self.bal_calulator_previous_years(['611','612','613','614','616','617']) ,
            })
            line_16 = self.env['esg.tfr.ligne'].search([('name','=','11. (+) Autres produits d\'exploitation'),('parent_id','=',rec.id)])
            line_16.write({
            'net':abs(self.bal_calulator_current_year(['718'])),
            'prev_net':abs(self.bal_calulator_previous_years(['718'])),
            })
            line_17 = self.env['esg.tfr.ligne'].search([('name','=','12. (-) Autres charges d\'exploitation'),('parent_id','=',rec.id)])
            line_17.write(
            {
            'net':self.bal_calulator_current_year(['618']) if self.bal_calulator_current_year(['618']) < 0 else - self.bal_calulator_current_year(['618']),
            'prev_net':self.bal_calulator_previous_years(['618']) if self.bal_calulator_previous_years(['618']) < 0  else  - self.bal_calulator_previous_years(['618']),
            })
            line_18 = self.env['esg.tfr.ligne'].search([('name','=','13. (+) Reprises d\'exploitation, transferts de charges'),('parent_id','=',rec.id)])
            line_18.write({
            'net':abs(self.bal_calulator_current_year(['719'])),
            'prev_net':abs(self.bal_calulator_previous_years(['719'])),
            })
            line_19 = self.env['esg.tfr.ligne'].search([('name','=','14. (-) Dotations d\'exploitation'),('parent_id','=',rec.id)])
            line_19.write({
            'net':self.bal_calulator_current_year(['619']) if self.bal_calulator_current_year(['619']) < 0 else - self.bal_calulator_current_year(['619']),
            'prev_net':self.bal_calulator_previous_years(['619']) if self.bal_calulator_previous_years(['619']) < 0 else - self.bal_calulator_previous_years(['619']),
            })

            line_20 = self.env['esg.tfr.ligne'].search([('name','=','VI. (=) RESULTAT D\'EXPLOITATION (+ou-)'),('parent_id','=',rec.id)])
            line_20.write({
            'net':self.bal_calulator_current_year(['71']) - self.bal_calulator_current_year(['61']),
            'prev_net':self.bal_calulator_previous_years(['71']) - self.bal_calulator_previous_years(['61']),
            })
            line_21 = self.env['esg.tfr.ligne'].search([('name','=','VII. (+/-) RESULTAT FINANCIER'),('parent_id','=',rec.id)])
            line_21.write({
            'net':self.bal_calulator_current_year(['73']) - self.bal_calulator_current_year(['63']),
            'prev_net':self.bal_calulator_previous_years(['73']) - self.bal_calulator_previous_years(['63']),
            })
            line_22 = self.env['esg.tfr.ligne'].search([('name','=','VIII. (=) RESULTAT COURANT (+ou-)'),('parent_id','=',rec.id)])
            line_22.write({
            'net':self.bal_calulator_current_year(['73','71']) - self.bal_calulator_current_year(['63','61']),
            'prev_net':self.bal_calulator_previous_years(['73','71']) - self.bal_calulator_previous_years(['63','61']),
            })

            line_23 = self.env['esg.tfr.ligne'].search([('name','=','IX. (+/-) RESULTAT NON COURANT'),('parent_id','=',rec.id)])
            line_23.write({
            'net':self.bal_calulator_current_year(['75']) - self.bal_calulator_current_year(['65']),
            'prev_net':self.bal_calulator_previous_years(['75']) - self.bal_calulator_previous_years(['65']),
            })
            line_24 = self.env['esg.tfr.ligne'].search([('name','=','15. (-) IMPOTS SUR LES RESULTATS'),('parent_id','=',rec.id)])
            line_24.write({
            'net':self.bal_calulator_current_year(['67']) if self.bal_calulator_current_year(['67']) < 0 else - self.bal_calulator_current_year(['67']),
            'prev_net':self.bal_calulator_previous_years(['67']) if self.bal_calulator_previous_years(['67']) < 0 else self.bal_calulator_previous_years(['67']),
            })
            line_25 = self.env['esg.tfr.ligne'].search([('name','=','X. (=) RESULTAT NET DE L\'EXERCICE'),('parent_id','=',rec.id)])
            line_25.write({
            'net':self.bal_calulator_current_year(['71','73','75']) - self.bal_calulator_current_year(['61','63','65','67']),
            'prev_net':self.bal_calulator_previous_years(['71','73','75']) - self.bal_calulator_previous_years(['61','63','65','67']),
            })
    
    def get_xml(self,parent):
        pass
class ESGTFRLignes(models.Model):
    _name = "esg.tfr.ligne"  

    name = fields.Char(string=u"Nom",required=True,readonly=True)
    net  = fields.Float(string=u"Net",readonly=True)
    prev_net  = fields.Float(string=u"Net d'exercice précédent",readonly=True)
    
    # Code edi Fields
    code_edi_net  = fields.Integer(string=u"Edi Net",readonly=True)
    code_edi_prev_net  = fields.Integer(string=u"Edi Net précédent",readonly=True)
    
    # Relational Fields
    parent_id = fields.Many2one(string='Parent Id', comodel_name='esg.tfr')
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('esg.tfr.ligne'))



