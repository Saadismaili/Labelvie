# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)


class PassagePassage(models.Model):
    _name = 'liasse.passage'
    _description = 'Passage'

    name = fields.Char(string=u"Nom",default="PASSAGE DU RESULTAT NET COMPTABLE AU RESULTAT NET FISCAL",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('liasse.passage'))
    # benifice and perte exercice
    benifice_net_1 = fields.Float(u'Bénéfice net comptable')
    perte_nette_1 = fields.Float(u'Perte nette comptable')
    # Relational fields
    re_fy_courante_ids = fields.One2many(comodel_name="passage.line1", inverse_name="passage_id", string="II. REINTEGRATIONS FISCALES COURANTE", required=False, copy=True,)
    re_fy_non_courante_ids = fields.One2many(comodel_name="passage.line2", inverse_name="passage_id", string="II. REINTEGRATIONS FISCALES NON COURANTE", required=False, copy=True,)
    de_fy_courante_ids = fields.One2many(comodel_name="passage.line3", inverse_name="passage_id", string="III. DEDUCTIONS FISCALES COURANTE", required=False, copy=True,)
    de_fy_non_courante_ids = fields.One2many(comodel_name="passage.line4", inverse_name="passage_id", string="III. DEDUCTIONS FISCALES NON COURANTE", required=False, copy=True,)
    reintegration_total = fields.Float(string="Total de REINTEGRATIONS")
    deduction_total = fields.Float(string="Total de DEDUCTIONS")
    # benifice and perte repport 1
    benifice_brut_1 = fields.Float(u'Bénéfice brut fiscal')
    deficit_brut_1 = fields.Float(u'Déficit brut fiscal')
    # amort and exercices fields reports
    exercice_n_4 = fields.Float(u'Exercice (n-4)')
    exercice_n_3 = fields.Float(u'Exercice (n-3)')
    exercice_n_2 = fields.Float(u'Exercice (n-2)')
    exercice_n_1 = fields.Float(u'Exercice (n-1)')
    amortissement = fields.Float(u'Amortissement')
    # benifice and perte repport
    benifice_net_a_c_1 = fields.Float(u'Bénéfice net fiscal (A-C)')
    deficit_net_b_1 = fields.Float(u'Déficit net fiscal (B)')
    # amort and exercices fields
    amortissement_1 = fields.Float(u'Cumul des amortissements fiscalement différés')
    exercice_n_4_1_c = fields.Float(u'CUMUL Exercice (n-4)')
    exercice_n_3_1_c = fields.Float(u'CUMUL Exercice (n-3)')
    exercice_n_2_1_c = fields.Float(u'CUMUL Exercice (n-2)')
    exercice_n_1_1_c = fields.Float(u'CUMUL Exercice (n-1)')
    
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    
    def create_lines(self):
        '''This function automatically assigne lignes from the passage repports that we show in our system'''
        for rec in self:
            rec.re_fy_courante_ids = [(5, 0, 0)]
            rec.re_fy_non_courante_ids = [(5, 0, 0)]
            rec.de_fy_courante_ids = [(5, 0, 0)]
            rec.de_fy_non_courante_ids = [(5, 0, 0)]
            for i in self.env['passage.line'].search([('group_id.sequence','=',30)]):
                self.env['passage.line1'].create({
                    'name':i.name,
                    'code':i.period_fiscal_year,
                    'passage_id':rec.id,
                })
            for i in self.env['passage.line'].search([('group_id.sequence','=',40)]):
                self.env['passage.line2'].create({
                    'name':i.name,
                    'code':i.period_fiscal_year,
                    'passage_id':rec.id,
                })
            for i in self.env['passage.line'].search([('group_id.sequence','=',60)]):
                self.env['passage.line3'].create({
                    'name':i.name,
                    'code':i.period_fiscal_year,
                    'passage_id':rec.id,
                })   
            for i in self.env['passage.line'].search([('group_id.sequence','=',70)]):
                self.env['passage.line4'].create({
                    'name':i.name,
                    'code':i.period_fiscal_year,
                    'passage_id':rec.id,
                })
    
    def from_string_to_list(self,val,list):
        '''This function converts from string Code to a list'''
        list = []
        for x in str(val):
            list.append(x)
        return list
    
    def list_verification(self,list1,list2):
        '''After we convert the code to the list we compare the two lists with function and we see if they matches'''
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
    
    def bal_calulator_current_year(self,codes,n=0):
        '''we return balance with this function, we just give it the code in a string format'''
        for rec in self:
            journal_entries = self.env['account.move'].search([('name','!=',False),('state','=','posted'),('company_id','=',self.env.company.id)])
            bal = 0
            item_code = col = []
            for code in codes:
                for entry in journal_entries:
                    if rec.fy_n_id:
                        for ref in rec.fy_n_id:
                            for item in entry.line_ids:
                                if ref.date_end.year - n == entry.date.year:
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
           
    def calculate_amortissement(self,cal_lines):
        '''This Function helps us to calculate ammort cumul and repport'''
        for rec in self:
            passage_data_2 = self.env['passage.enterieur'].search([('company_id','=',self.env.company.id)])    
            passage_data = self.env['passage.enterieur'].search([('company_id','=',self.env.company.id),('date','>=',rec.fy_n_id.date_start),('date','<=',rec.fy_n_id.date_end)])    
            cumul_mouvements = self.env['account.move'].search([('date','<=',rec.fy_n_id.date_end),('state','=','posted'),('company_id','=',self.env.company.id)],order="date asc")
            cumul_final = 0
            enterieur = 0                 
            var_cal = 0
            if passage_data_2 and passage_data_2.date.year < rec.fy_n_id.date_end.year:
                enterieur = passage_data_2.cumule_amorti 
            for move in cumul_mouvements:
                sum_619 = 0
                sum_charge_net = 0
                sum_prod_net = 0
                if move.date.year < rec.fy_n_id.date_end.year:
                    for line in move.line_ids:
                        if str(line.account_id.code[0] + line.account_id.code[1] + line.account_id.code[2]) == '619':
                            sum_619 += line.debit - line.credit
                        if str(line.account_id.code[0] + line.account_id.code[1]) in ['73','75','71'] :
                            sum_prod_net += line.debit - line.credit 
                        if str(line.account_id.code[0] + line.account_id.code[1]) in ['63','65','67','61']:
                            sum_charge_net += line.debit - line.credit
                    if ( abs(sum_prod_net) - abs(sum_charge_net))  < 0 :
                        if  abs(abs(sum_prod_net) - abs(sum_charge_net)) > sum_619 :
                            if passage_data_2 and passage_data_2.date.year == rec.fy_n_id.date_end.year - 1 :
                                var_cal =  passage_data_2.exercice_n_3 + passage_data_2.exercice_n_2 + passage_data_2.exercice_n_1
                                if  move.date.year == rec.fy_n_id.date_end.year - 1:
                                    var_cal += abs(sum_prod_net) - abs(sum_charge_net) - sum_619 
                            elif passage_data_2 and passage_data_2.date.year == rec.fy_n_id.date_end.year - 2 :
                                var_cal = passage_data_2.exercice_n_2 + passage_data_2.exercice_n_1
                                if move.date.year== rec.fy_n_id.date_end.year - 2 or move.date.year== rec.fy_n_id.date_end.year - 1:
                                    var_cal += abs(sum_prod_net) - abs(sum_charge_net) - sum_619
                            elif passage_data_2 and passage_data_2.date.year == rec.fy_n_id.date_end.year - 3 :
                                var_cal =  passage_data_2.exercice_n_2 + passage_data_2.exercice_n_1
                                if move.date.year== rec.fy_n_id.date_end.year - 3 or move.date.year== rec.fy_n_id.date_end.year - 2 or move.date.year== rec.fy_n_id.date_end.year - 1:
                                    var_cal += abs(sum_prod_net) - abs(sum_charge_net) - sum_619
                            elif move.date.year>= rec.fy_n_id.date_end.year -4 :
                                var_cal += abs(sum_prod_net) - abs(sum_charge_net) - sum_619
                            cumul_final += sum_619
                            rec.amortissement_1 = cumul_final + enterieur
                            rec.amortissement = 0
                        else:
                            cumul_final += abs(sum_prod_net - sum_charge_net)
                            rec.amortissement_1 = cumul_final + enterieur
                            rec.amortissement = 0
                    else :
                        if  abs(sum_prod_net) - abs(sum_charge_net) - abs(var_cal) - cal_lines  >= cumul_final + enterieur :
                            rec.amortissement_1 = 0
                            rec.amortissement = cumul_final + enterieur
                            cumul_final = 0
                            if passage_data_2 and  passage_data_2.date.year < move.date.year:
                                enterieur = 0
                            
                        else:
                            rec.amortissement_1 = cumul_final + enterieur
                            rec.amortissement = 0
                elif move.date.year == rec.fy_n_id.date_end.year:
                    for line in move.line_ids:
                        if str(line.account_id.code[0] + line.account_id.code[1] + line.account_id.code[2]) == '619':
                            sum_619 += line.debit - line.credit
                        if str(line.account_id.code[0] + line.account_id.code[1]) in ['73','75','71'] :
                            sum_prod_net += line.debit - line.credit 
                        if str(line.account_id.code[0] + line.account_id.code[1]) in ['63','65','67','61']:
                            sum_charge_net += line.debit - line.credit
                    if abs(sum_prod_net) - abs(sum_charge_net) > 0:
                        if  abs(sum_prod_net) - abs(sum_charge_net) - abs(var_cal) - cal_lines  >= cumul_final + enterieur :
                                rec.amortissement_1 = 0
                                rec.amortissement = cumul_final + enterieur
                                cumul_final = 0
                                enterieur = 0
                        
            if passage_data:
                rec.amortissement_1 = passage_data.cumule_amorti 
                rec.amortissement = 0  
                
                    
    def get_lines(self):
        '''This is a principal Function that calculates all fields in this model'''
        for rec in self:
            cal = 0
            val = val_1 = val_2 = val_3  = 0
            rec.create_lines()
            for line in rec.re_fy_courante_ids : 
                if line.name == '- Achats, Travaux et prestations de service sur exercices antérieurs (omissions)':
                    self.env['passage.line1'].search([('id','=',line.id)]).write({
                        'montant_1':rec.bal_calulator_current_year(['6118','6128','6148','6168','6178','6188','6198','6318','6338','6388','6398'],0),
                    })
                else:
                    self.env['passage.line1'].search([('id','=',line.id)]).write({
                        'montant_1':self.env['account.move.line'].search([('disallowed_expense_id.code','=',line.code),('date','<=',rec.fy_n_id.date_end),('date','>=',rec.fy_n_id.date_end)]).disallowed_price,
                    })
            for line in rec.re_fy_non_courante_ids :
                if line.name == '- Autres charges non courantes et/ou sur exercices antérieurs':
                    self.env['passage.line2'].search([('id','=',line.id)]).write({
                        'montant_1':rec.bal_calulator_current_year(['6518','6568','6588','6598'],0),
                    })
                elif line.name == '- Impôts sur les résultats':
                    self.env['passage.line2'].search([('id','=',line.id)]).write({
                        'montant_1' : rec.bal_calulator_current_year(['67'],0),
                    })
                else:
                    self.env['passage.line2'].search([('id','=',line.id)]).write({
                            'montant_1' : self.env['account.move.line'].search([('disallowed_expense_id.code','=',line.code),('date','<=',rec.fy_n_id.date_end),('date','>=',rec.fy_n_id.date_end)]).disallowed_price,
                        })
            for line in rec.de_fy_courante_ids :
                if line.name == '- Revenu des titres de participation compte 7321 si exonérés, (art. 6 du CGI).':
                    self.env['passage.line3'].search([('id','=',line.id)]).write({
                        'montant_1' : rec.bal_calulator_current_year(['7321'],0),
                    })
                elif line.name=='- Revenu des titres immobilisés Compte 7325 si exonérés, (art. 6 du CGI).':
                    self.env['passage.line3'].search([('id','=',line.id)]).write({
                        'montant_1' : rec.bal_calulator_current_year(['7325'],0),
                    })
                elif line.name == '- Profit latent de change (Ecarts de conversion) solde au 31-12-N-1 (Comptes : 17 et 47)':
                    self.env['passage.line3'].search([('id','=',line.id)]).write({
                        'montant_1' : rec.bal_calulator_current_year(['17','47'],0),
                    })
                elif line.name == '- Indemnités de retard Comptabilisées non encaissées au 31/12/N (compte 73811)':
                    self.env['passage.line3'].search([('id','=',line.id)]).write({
                        'montant_1' : rec.bal_calulator_current_year(['73811'],0),
                    })
                elif line.name == '- Indemnités de retard Comptabilisées non payées au 31/12/N-1 (compte 63118)':
                    self.env['passage.line3'].search([('id','=',line.id)]).write({
                        'montant_1' : rec.bal_calulator_current_year(['63118'],0),
                    }) 
                else:
                    self.env['passage.line3'].search([('id','=',line.id)]).write({
                        'montant_1':self.env['account.move.line'].search([('disallowed_expense_id.code','=',line.code),('date','<=',rec.fy_n_id.date_end),('date','>=',rec.fy_n_id.date_end)]).disallowed_price,
                    })
            for line in rec.de_fy_non_courante_ids : 
                self.env['passage.line4'].search([('id','=',line.id)]).write({
                        'montant_1':self.env['account.move.line'].search([('disallowed_expense_id.code','=',line.code),('date','<=',rec.fy_n_id.date_end),('date','>=',rec.fy_n_id.date_end)]).disallowed_price,
                    })
            reintegration = 0           
            deduction = 0           
            for line in rec.re_fy_courante_ids:
                reintegration += line.montant_1
                cal += line.montant_1
            for line in rec.re_fy_non_courante_ids:
                reintegration += line.montant_1
                cal += line.montant_1
            for line in rec.de_fy_courante_ids:
                deduction += line.montant_1
                cal -= line.montant_1
            for line in rec.de_fy_non_courante_ids:
                deduction += line.montant_1
                cal -= line.montant_1
            rec.reintegration_total = reintegration
            rec.deduction_total = deduction
            net = rec.bal_calulator_current_year(['71','73','75'],0) - rec.bal_calulator_current_year(['61','63','65','67'],0)
            rec.benifice_net_1 =  net if net > 0 else 0
            rec.perte_nette_1 =  abs(net) if net < 0 else 0
            rec.benifice_brut_1 = rec.benifice_net_1 + cal if rec.benifice_net_1 > 0 else 0
            rec.deficit_brut_1 = rec.perte_nette_1 - cal if rec.perte_nette_1 > 0 else 0
            rec.benifice_net_a_c_1 = rec.benifice_brut_1
            rec.deficit_net_b_1 = rec.deficit_brut_1
            
            passage_enterieur = self.env['passage.enterieur'].search([('id','!=',False),('company_id','=',self.env.company.id)])
            if passage_enterieur.exists():
                if rec.fy_n_id.date_end.year == passage_enterieur.date.year:
                    rec.exercice_n_4_1_c = passage_enterieur.exercice_n_4
                    rec.exercice_n_3_1_c = passage_enterieur.exercice_n_3
                    rec.exercice_n_2_1_c = passage_enterieur.exercice_n_2
                    rec.exercice_n_1_1_c = passage_enterieur.exercice_n_1
                elif rec.fy_n_id.date_end.year != passage_enterieur.date.year: 
                    if rec.fy_n_id.date_end.year - 1== passage_enterieur.date.year :
                        rec.exercice_n_4_1_c = passage_enterieur.exercice_n_3
                        rec.exercice_n_3_1_c = passage_enterieur.exercice_n_2
                        rec.exercice_n_2_1_c = passage_enterieur.exercice_n_1
                        rec.exercice_n_1_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) - abs(rec.bal_calulator_current_year(['619'],1)) if (rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) > abs(rec.bal_calulator_current_year(['619'],1)) else 0                                 
                    elif rec.fy_n_id.date_end.year - 2== passage_enterieur.date.year :
                        net_1 = rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2) 
                        net_619_1 = rec.bal_calulator_current_year(['619'],1)
                        rec.exercice_n_4_1_c = passage_enterieur.exercice_n_2
                        rec.exercice_n_3_1_c = passage_enterieur.exercice_n_1
                        rec.exercice_n_2_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2)) - abs(rec.bal_calulator_current_year(['619'],2)) if (rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2)) > abs(rec.bal_calulator_current_year(['619'],2)) else 0
                        rec.exercice_n_1_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) - abs(rec.bal_calulator_current_year(['619'],1)) if (rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) > abs(rec.bal_calulator_current_year(['619'],1)) else 0
                    elif rec.fy_n_id.date_end.year - 3== passage_enterieur.date.year :
                        net_1 = rec.bal_calulator_current_year(['71','73','75'],3) - rec.bal_calulator_current_year(['61','63','65','67'],3) 
                        net_619_1 = rec.bal_calulator_current_year(['619'],3)
                        rec.exercice_n_4_1_c = passage_enterieur.exercice_n_1
                        rec.exercice_n_3_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],3) - rec.bal_calulator_current_year(['61','63','65','67'],3)) - abs(rec.bal_calulator_current_year(['619'],3)) if (rec.bal_calulator_current_year(['71','73','75'],3) - rec.bal_calulator_current_year(['61','63','65','67'],3)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],3) - rec.bal_calulator_current_year(['61','63','65','67'],3)) > abs(rec.bal_calulator_current_year(['619'],3)) else 0
                        rec.exercice_n_2_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2)) - abs(rec.bal_calulator_current_year(['619'],2)) if (rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2)) > abs(rec.bal_calulator_current_year(['619'],2)) else 0
                        rec.exercice_n_1_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) - abs(rec.bal_calulator_current_year(['619'],1)) if (rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) > abs(rec.bal_calulator_current_year(['619'],1)) else 0
                    else:
                        rec.exercice_n_4_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],4) - rec.bal_calulator_current_year(['61','63','65','67'],4)) - abs(rec.bal_calulator_current_year(['619'],4)) if (rec.bal_calulator_current_year(['71','73','75'],4) - rec.bal_calulator_current_year(['61','63','65','67'],4)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],4) - rec.bal_calulator_current_year(['61','63','65','67'],4)) > abs(rec.bal_calulator_current_year(['619'],4)) else 0
                        rec.exercice_n_3_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],3) - rec.bal_calulator_current_year(['61','63','65','67'],3)) - abs(rec.bal_calulator_current_year(['619'],3)) if (rec.bal_calulator_current_year(['71','73','75'],3) - rec.bal_calulator_current_year(['61','63','65','67'],3)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],3) - rec.bal_calulator_current_year(['61','63','65','67'],3)) > abs(rec.bal_calulator_current_year(['619'],3)) else 0
                        rec.exercice_n_2_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2)) - abs(rec.bal_calulator_current_year(['619'],2)) if (rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2)) > abs(rec.bal_calulator_current_year(['619'],2)) else 0
                        rec.exercice_n_1_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) - abs(rec.bal_calulator_current_year(['619'],1)) if (rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) > abs(rec.bal_calulator_current_year(['619'],1)) else 0
            else:
                rec.exercice_n_4_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],4) - rec.bal_calulator_current_year(['61','63','65','67'],4)) - abs(rec.bal_calulator_current_year(['619'],4)) if (rec.bal_calulator_current_year(['71','73','75'],4) - rec.bal_calulator_current_year(['61','63','65','67'],4)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],4) - rec.bal_calulator_current_year(['61','63','65','67'],4)) > abs(rec.bal_calulator_current_year(['619'],4)) else 0
                rec.exercice_n_3_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],3) - rec.bal_calulator_current_year(['61','63','65','67'],3)) - abs(rec.bal_calulator_current_year(['619'],3)) if (rec.bal_calulator_current_year(['71','73','75'],3) - rec.bal_calulator_current_year(['61','63','65','67'],3)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],3) - rec.bal_calulator_current_year(['61','63','65','67'],3)) > abs(rec.bal_calulator_current_year(['619'],3)) else 0
                rec.exercice_n_2_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2)) - abs(rec.bal_calulator_current_year(['619'],2)) if (rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],2) - rec.bal_calulator_current_year(['61','63','65','67'],2)) > abs(rec.bal_calulator_current_year(['619'],2)) else 0
                rec.exercice_n_1_1_c = abs(rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) - abs(rec.bal_calulator_current_year(['619'],1)) if (rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) < 0 and abs(rec.bal_calulator_current_year(['71','73','75'],1) - rec.bal_calulator_current_year(['61','63','65','67'],1)) > abs(rec.bal_calulator_current_year(['619'],1)) else 0
            if rec.benifice_brut_1 > 0:
                if rec.benifice_brut_1 - rec.exercice_n_4_1_c  > 0:
                    val = rec.benifice_brut_1 - rec.exercice_n_4_1_c
                    rec.exercice_n_4 = rec.exercice_n_4_1_c
                    rec.exercice_n_4_1_c = 0
                if val - rec.exercice_n_3_1_c > 0:
                    val_1 = val - rec.exercice_n_3_1_c
                    rec.exercice_n_3 = rec.exercice_n_3_1_c
                    rec.exercice_n_3_1_c = 0
                if val_1 - rec.exercice_n_2_1_c > 0:
                    val_2 = val_1 - rec.exercice_n_2_1_c
                    rec.exercice_n_2 = rec.exercice_n_2_1_c
                    rec.exercice_n_2_1_c = 0
                if val_2 - rec.exercice_n_1_1_c > 0:
                    val_3 = val_2 - rec.exercice_n_1_1_c
                    rec.exercice_n_1 = rec.exercice_n_1_1_c
                    rec.exercice_n_1_1_c = 0
            rec.calculate_amortissement(cal)    
            
    def get_xml(self,parent):
        for rec in self:
            tableau = etree.SubElement(parent, "tableau")
            etree.SubElement(tableau,"id").text = str(7)
            group_valeurs = etree.SubElement(parent, "groupeValeurs")
            # Benifice
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(817)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.benifice_net_1)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(819)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            # Perte
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(818)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(820)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.perte_nette_1)
            # Repport  Reigtegration 
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(18009)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.reintegration_total)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(18010)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            if rec.re_fy_courante_ids:
                i=0
                for line in rec.re_fy_courante_ids:
                    i+=1
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(821)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.name)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(822)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_1)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(823)
                    etree.SubElement(valeur_cellule, "valeur").text = str(0)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
            if rec.re_fy_non_courante_ids:
                i=0
                for line in rec.re_fy_non_courante_ids:
                    i+=1
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(824)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.name)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(825)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_1)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(826)
                    etree.SubElement(valeur_cellule, "valeur").text = str(0)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
            # Repport  Deduction 
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(18012)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(18013)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.deduction_total)
            if rec.de_fy_courante_ids:
                i=0       
                for line in rec.de_fy_courante_ids:
                    i+=1
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(827)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.name)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(828)
                    etree.SubElement(valeur_cellule, "valeur").text = str(0)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(830)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_1)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
            if rec.de_fy_non_courante_ids:
                i=0
                for line in rec.de_fy_non_courante_ids:
                    i+=1
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(829)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.name)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(831)
                    etree.SubElement(valeur_cellule, "valeur").text = str(0)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(7830)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_1)
                    etree.SubElement(valeur_cellule, "numeroLigne").text = str(i)
            # Repport  Total 
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(833)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.reintegration_total + rec.benifice_net_1)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(834)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.deduction_total + rec.perte_nette_1)
            # Repport  benifice_brut_1 
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(837)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.benifice_brut_1)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(839)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            # Repport deficit_brut_1
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(838)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(840)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.deficit_brut_1)
            # Repport  exer 4
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(845)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.exercice_n_4)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(849)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            # Repport  exer 3
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(846)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.exercice_n_3)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(850)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            # Repport  exer 2
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(847)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.exercice_n_2)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(851)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            # Repport  exer 1
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(848)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.exercice_n_1)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(852)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            # Repport  Bénéfice net fiscal ( A - C) (OU)  
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(6872)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.benifice_net_a_c_1)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(6874)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            # Repport . Déficit net fiscal (B) 
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(6873)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(6875)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.deficit_net_b_1)
            # CUMUL DES AMORTISSEMENTS FISCALEMENT DIFFERES 
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(854)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.amortissement_1)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(855)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            # Cumul  exer 4
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(860)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.exercice_n_4_1_c)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(864)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            # Cumul  exer 3
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(861)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.exercice_n_3_1_c)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(865)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            # Cumul  exer 2
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(862)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.exercice_n_2_1_c)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(866)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            # Cumul  exer 1
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(863)
            etree.SubElement(valeur_cellule, "valeur").text = str(rec.exercice_n_1_1_c)
            valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
            cellule = etree.SubElement(valeur_cellule, "cellule")
            etree.SubElement(cellule, "codeEdi").text = str(867)
            etree.SubElement(valeur_cellule, "valeur").text = str(0)
            extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")

class passageLine1(models.Model):
    _name = 'passage.line1'
    _description = 'Passage line 1'

    name = fields.Char(string=u"Description",required=True,)
    montant_1 = fields.Float(string=u"Montant",  required=False, )
    code  = fields.Char(string='Code de référence')
    passage_id = fields.Many2one(comodel_name="liasse.passage", string="Passage", required=False, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('passage.line1'))

class passageLine2(models.Model):
    _name = 'passage.line2'
    _description = 'Passage line 2'

    name = fields.Char(string=u"Description",required=True,)
    montant_1 = fields.Float(string=u"Montant",  required=False, )
    code  = fields.Char(string='Code de référence')
    passage_id = fields.Many2one(comodel_name="liasse.passage", string="Passage", required=False, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('passage.line2'))

class passageLine3(models.Model):
    _name = 'passage.line3'
    _description = 'Passage line 3'

    name = fields.Char(string=u"Description", required=True,)
    montant_1 = fields.Float(string=u"Montant",  required=False, )
    code  = fields.Char(string='Code de référence')
    passage_id = fields.Many2one(comodel_name="liasse.passage", string="Passage", required=False, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('passage.line3'))

class passageLine4(models.Model):
    _name = 'passage.line4'
    _description = 'Passage line 4'

    name = fields.Char(string=u"Description", required=True,)
    montant_1 = fields.Float(string=u"Montant",  required=False, )
    code  = fields.Char(string='Code de référence')
    passage_id = fields.Many2one(comodel_name="liasse.passage", string="Passage", required=False, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('passage.line4'))