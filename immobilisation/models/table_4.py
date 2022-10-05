# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)

class Tablefour(models.Model):
    _name = 'immo.financiere'
    _description = 'TABLEAU DES IMMOBILISATIONS AUTRES QUE FINANCIERES'

    name = fields.Char(string=u"Nom",default="IMMOBILISATIONS AUTRES QUE FINANCIERES",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False,store=True,)
    line_ids = fields.One2many(string='Lignes',comodel_name='immo.financiere.line',inverse_name='immo_id' )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('immo.financiere'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    
    def print_pdf(self):
        return self.env.ref('immobilisation.action_report_immo_financiere').report_action(self, config=False)

    @api.model
    def create(self, values):
        return super(Tablefour,self).create({
            'line_ids' : self.env['immo.financiere.line'].create([{'name':'IMMOBILISATION EN NON-VALEURS','edi_montant_start' :10064 , 'edi_augmentation_acquisition': 10065, 'edi_augmentation_production' :10066 , 'edi_augmentation_transaction': 10067,'edi_diminution_cession':10068 , 'edi_diminution_withdrawal':10069 ,'edi_diminution_transaction': 10070, 'edi_montant_end' :10071 ,'code':'111','immo_id':self.id,},
                                                                  {'name':'* Frais préliminaires','edi_montant_start' :966 , 'edi_augmentation_acquisition': 980, 'edi_augmentation_production' :994 , 'edi_augmentation_transaction': 1008,'edi_diminution_cession':1022 , 'edi_diminution_withdrawal':1036 ,'edi_diminution_transaction': 1050, 'edi_montant_end' :1064 ,'code':'1','immo_id':self.id,},
                                                                  {'name':'* Charges à répartir sur plusieurs exercices','edi_montant_start' :967 , 'edi_augmentation_acquisition': 981, 'edi_augmentation_production' :995 , 'edi_augmentation_transaction': 1009,'edi_diminution_cession':1023 , 'edi_diminution_withdrawal':1037 ,'edi_diminution_transaction': 1051, 'edi_montant_end' :1065 ,'code':'2','immo_id':self.id,},                                                               
                                                                  {'name':'* Primes des rembourssement des obligations','edi_montant_start' :968 , 'edi_augmentation_acquisition': 982, 'edi_augmentation_production' :996 , 'edi_augmentation_transaction': 1010,'edi_diminution_cession':1024 , 'edi_diminution_withdrawal':1038 ,'edi_diminution_transaction': 1052, 'edi_montant_end' :1066 ,'code':'0','immo_id':self.id,},
                                                                  {'name':'IMMOBILISATIONS INCORPORELLES','edi_montant_start' :10073 , 'edi_augmentation_acquisition': 10074, 'edi_augmentation_production' :10075 , 'edi_augmentation_transaction': 10076,'edi_diminution_cession':10077 , 'edi_diminution_withdrawal':10078 ,'edi_diminution_transaction': 10079, 'edi_montant_end' :10080 ,'code':'222','immo_id':self.id,},
                                                                  {'name':'* Immobilisation en recherche et développement +','edi_montant_start' :969 , 'edi_augmentation_acquisition': 983, 'edi_augmentation_production' :997 , 'edi_augmentation_transaction': 1011,'edi_diminution_cession':1025 , 'edi_diminution_withdrawal':1039 ,'edi_diminution_transaction': 1053, 'edi_montant_end' :1067 ,'code':'3','immo_id':self.id,},
                                                                  {'name':'* Brevets, marques droits et valeurs similairest','edi_montant_start' :970 , 'edi_augmentation_acquisition': 984, 'edi_augmentation_production' :998 , 'edi_augmentation_transaction': 1012,'edi_diminution_cession':1026 , 'edi_diminution_withdrawal':1040 ,'edi_diminution_transaction': 1054, 'edi_montant_end' :1068 ,'code':'4','immo_id':self.id,},
                                                                  {'name':'* Fonds commercial','edi_montant_start' :971 , 'edi_augmentation_acquisition': 985, 'edi_augmentation_production' :999 , 'edi_augmentation_transaction': 1013,'edi_diminution_cession':1027 , 'edi_diminution_withdrawal':1041 ,'edi_diminution_transaction': 1055, 'edi_montant_end' :1069 ,'code':'5','immo_id':self.id,},
                                                                  {'name':'* Autres immobilisations incorporelles','edi_montant_start' :972 , 'edi_augmentation_acquisition': 986, 'edi_augmentation_production' :1000 , 'edi_augmentation_transaction': 1014,'edi_diminution_cession':1028 , 'edi_diminution_withdrawal':1042 ,'edi_diminution_transaction': 1056, 'edi_montant_end' :1070 ,'code':'6','immo_id':self.id,},
                                                                  {'name':'IMMOBILISATIONS CORPORELLES','edi_montant_start' :10082 , 'edi_augmentation_acquisition': 10083, 'edi_augmentation_production' :10084 , 'edi_augmentation_transaction': 10085,'edi_diminution_cession':10086 , 'edi_diminution_withdrawal':10087 ,'edi_diminution_transaction': 10088, 'edi_montant_end' :10089 ,'code':'333','immo_id':self.id,},
                                                                  {'name':'* Terrains','edi_montant_start' :973 , 'edi_augmentation_acquisition': 987, 'edi_augmentation_production' :1001 , 'edi_augmentation_transaction': 1015,'edi_diminution_cession':1029 , 'edi_diminution_withdrawal':1043 ,'edi_diminution_transaction': 1057, 'edi_montant_end' :1071 ,'code':'7','immo_id':self.id,},
                                                                  {'name':'* Constructions','edi_montant_start' :974 , 'edi_augmentation_acquisition': 988, 'edi_augmentation_production' :1002 , 'edi_augmentation_transaction': 1016,'edi_diminution_cession':1030 , 'edi_diminution_withdrawal':1044 ,'edi_diminution_transaction': 1058, 'edi_montant_end' :1072 ,'code':'8','immo_id':self.id,},
                                                                  {'name':'* Installations techniques; matériel et outillage','edi_montant_start' :975 , 'edi_augmentation_acquisition': 989, 'edi_augmentation_production' :1003 , 'edi_augmentation_transaction': 1017,'edi_diminution_cession':1031 , 'edi_diminution_withdrawal':1045 ,'edi_diminution_transaction': 1059, 'edi_montant_end' :1073 ,'code':'9','immo_id':self.id,},
                                                                  {'name':'* Matériel de transport','edi_montant_start' :976 , 'edi_augmentation_acquisition': 990, 'edi_augmentation_production' :1004 , 'edi_augmentation_transaction': 1018,'edi_diminution_cession':1032 , 'edi_diminution_withdrawal':1046 ,'edi_diminution_transaction': 1060, 'edi_montant_end' :1074 ,'code':'10','immo_id':self.id,},
                                                                  {'name':'* Mobilier, matériel de bureau et aménagements','edi_montant_start' :978 , 'edi_augmentation_acquisition': 992, 'edi_augmentation_production' :1006 , 'edi_augmentation_transaction': 1020,'edi_diminution_cession':1034 , 'edi_diminution_withdrawal':1048 ,'edi_diminution_transaction': 1062, 'edi_montant_end' :1076 ,'code':'11','immo_id':self.id,},
                                                                  {'name':'* Autres immobilisations corporelles','edi_montant_start' :979 , 'edi_augmentation_acquisition': 993, 'edi_augmentation_production' :1007 , 'edi_augmentation_transaction': 1021,'edi_diminution_cession':1035 , 'edi_diminution_withdrawal':1049 ,'edi_diminution_transaction': 1063, 'edi_montant_end' :1077 ,'code':'12','immo_id':self.id,},
                                                                  {'name':'* Immobilisations corporelles en cours','edi_montant_start' :977 , 'edi_augmentation_acquisition': 991, 'edi_augmentation_production' :1005 , 'edi_augmentation_transaction': 1019,'edi_diminution_cession':1033 , 'edi_diminution_withdrawal':1047 ,'edi_diminution_transaction': 1061, 'edi_montant_end' :1075 ,'code':'13','immo_id':self.id,},
                                                                  {'name':'TOTAL GENERAL',  'code':'444','immo_id':self.id,}
                                                                  ]),})

    def get_headers(self):
        """This Function calculates Table 4 head-Lines with its affectations"""
        for rec in self:
            assets = self.env['account.asset.asset'].search([('id','!=',False),('company_id','=',self.env.company.id)])
            if rec.line_ids:
                for line in rec.line_ids:
                    sum_1_acqui = sum_1_prod = sum_1_atran  = sum_1_cessi = sum_1_withd = sum_1_ctran = sum_1_start = sum_1_end = 0
                    sum_2_acqui = sum_2_prod = sum_2_atran  = sum_2_cessi = sum_2_withd = sum_2_ctran = sum_2_start = sum_2_end = 0
                    sum_3_acqui = sum_3_prod = sum_3_atran  = sum_3_cessi = sum_3_withd = sum_3_ctran = sum_3_start = sum_3_end = 0
                    sum_4_acqui = sum_4_prod = sum_4_atran  = sum_4_cessi = sum_4_withd = sum_4_ctran = sum_4_start = sum_4_end = 0
                    for asset in assets:
                        if not asset.date_cession or asset.date_cession.year > rec.fy_n_id.date_end.year:
                            if asset.category_id.account_type in ['0','1','2'] and line.code =='111':
                                if asset.invoice_date.year == rec.fy_n_id.date_end.year:
                                    if asset.acquisition_mode == 'a':
                                        sum_1_acqui += asset.value
                                    elif asset.acquisition_mode == 'p':
                                        sum_1_prod += asset.value
                                    elif asset.acquisition_mode == 'v':
                                        sum_1_atran += asset.value
                                elif asset.invoice_date.year < rec.fy_n_id.date_end.year:
                                    sum_1_start += asset.value
                                sum_1_end = sum_1_start + (sum_1_acqui + sum_1_prod + sum_1_atran) - sum_1_cessi - sum_1_withd - sum_1_ctran
                                line.augmentation_acquisition = sum_1_acqui
                                line.augmentation_production = sum_1_prod
                                line.augmentation_transaction = sum_1_atran
                                line.diminution_cession = sum_1_cessi
                                line.diminution_withdrawal = sum_1_withd
                                line.diminution_transaction = sum_1_ctran
                                line.montant_start = sum_1_start
                                line.montant_end = sum_1_end
                            if asset.category_id.account_type in ['3','4','5','6'] and line.code =='222':
                                if asset.invoice_date.year == rec.fy_n_id.date_end.year:
                                    if asset.acquisition_mode == 'a':
                                        sum_2_acqui += asset.value
                                    elif asset.acquisition_mode == 'p':
                                        sum_2_prod += asset.value
                                    elif asset.acquisition_mode == 'v':
                                        sum_2_atran += asset.value
                                elif asset.invoice_date.year < rec.fy_n_id.date_end.year:
                                    sum_2_start += asset.value
                                sum_2_end = sum_2_start + (sum_2_acqui + sum_2_prod + sum_2_atran) - sum_2_cessi - sum_2_withd - sum_2_ctran
                                line.augmentation_acquisition = sum_2_acqui
                                line.augmentation_production = sum_2_prod
                                line.augmentation_transaction = sum_2_atran
                                line.diminution_cession = sum_2_cessi
                                line.diminution_withdrawal = sum_2_withd
                                line.diminution_transaction = sum_2_ctran
                                line.montant_start = sum_2_start
                                line.montant_end = sum_2_end
                            if asset.category_id.account_type in ['7','8','9','10','11','12','13']  and line.code =='333':
                                if asset.invoice_date.year == rec.fy_n_id.date_end.year:
                                    if asset.acquisition_mode == 'a':
                                        sum_3_acqui += asset.value
                                    elif asset.acquisition_mode == 'p':
                                        sum_3_prod += asset.value
                                    elif asset.acquisition_mode == 'v':
                                        sum_3_atran += asset.value
                                elif asset.invoice_date.year < rec.fy_n_id.date_end.year:
                                    sum_3_start += asset.value
                                sum_3_end = sum_3_start + (sum_3_acqui + sum_3_prod + sum_3_atran) - sum_3_cessi - sum_3_withd - sum_3_ctran
                                line.augmentation_acquisition = sum_3_acqui
                                line.augmentation_production = sum_3_prod
                                line.augmentation_transaction = sum_3_atran
                                line.diminution_cession = sum_3_cessi
                                line.diminution_withdrawal = sum_3_withd
                                line.diminution_transaction = sum_3_ctran
                                line.montant_start = sum_3_start
                                line.montant_end = sum_3_end
                            if asset.category_id.account_type in ['0','1','2','3','4','5','6','7','8','9','10','11','12','13'] and line.code =='444':
                                if asset.invoice_date.year == rec.fy_n_id.date_end.year:
                                    if asset.acquisition_mode == 'a':
                                        sum_4_acqui += asset.value
                                    elif asset.acquisition_mode == 'p':
                                        sum_4_prod += asset.value
                                    elif asset.acquisition_mode == 'v':
                                        sum_4_atran += asset.value
                                elif asset.invoice_date.year < rec.fy_n_id.date_end.year:
                                    sum_4_start += asset.value
                                sum_4_end = sum_4_start + (sum_4_acqui + sum_4_prod + sum_4_atran) - sum_4_cessi - sum_4_withd - sum_4_ctran
                                line.augmentation_acquisition = sum_4_acqui
                                line.augmentation_production = sum_4_prod
                                line.augmentation_transaction = sum_4_atran
                                line.diminution_cession = sum_4_cessi
                                line.diminution_withdrawal = sum_4_withd
                                line.diminution_transaction = sum_4_ctran
                                line.montant_start = sum_4_start
                                line.montant_end = sum_4_end
                                
                        elif asset.date_cession.year == rec.fy_n_id.date_end.year:
                            if asset.category_id.account_type in ['1','2'] and line.code =='111':
                                if asset.invoice_date.year == rec.fy_n_id.date_end.year:
                                    if asset.acquisition_mode == 'a':
                                        sum_1_acqui += asset.value
                                    elif asset.acquisition_mode == 'p':
                                        sum_1_prod += asset.value
                                    elif asset.acquisition_mode == 'v':
                                        sum_1_atran += asset.value
                                if asset.mode_session == 'c':
                                    sum_1_cessi += asset.value
                                elif asset.mode_session == 'r':
                                    sum_1_withd += asset.value
                                elif asset.mode_session == 'v':
                                    sum_1_ctran += asset.value
                                elif asset.invoice_date.year < rec.fy_n_id.date_end.year:
                                    sum_1_start += asset.value
                                sum_1_end = sum_1_start + (sum_1_acqui + sum_1_prod + sum_1_atran) - sum_1_cessi - sum_1_withd - sum_1_ctran
                                line.augmentation_acquisition = sum_1_acqui
                                line.augmentation_production = sum_1_prod
                                line.augmentation_transaction = sum_1_atran
                                line.diminution_cession = sum_1_cessi
                                line.diminution_withdrawal = sum_1_withd
                                line.diminution_transaction = sum_1_ctran
                                line.montant_start = sum_1_start
                                line.montant_end = sum_1_end
                            if asset.category_id.account_type in ['3','4','5','6'] and line.code =='222':
                                if asset.invoice_date.year == rec.fy_n_id.date_end.year:
                                    if asset.acquisition_mode == 'a':
                                        sum_2_acqui += asset.value
                                    elif asset.acquisition_mode == 'p':
                                        sum_2_prod += asset.value
                                    elif asset.acquisition_mode == 'v':
                                        sum_2_atran += asset.value
                                if asset.mode_session == 'c':
                                    sum_2_cessi += asset.value
                                elif asset.mode_session == 'r':
                                    sum_2_withd += asset.value
                                elif asset.mode_session == 'v':
                                    sum_2_ctran += asset.value
                                elif asset.invoice_date.year < rec.fy_n_id.date_end.year:
                                    sum_2_start += asset.value
                                sum_2_end = sum_2_start + (sum_2_acqui + sum_2_prod + sum_2_atran) - sum_2_cessi - sum_2_withd - sum_2_ctran
                                line.augmentation_acquisition = sum_2_acqui
                                line.augmentation_production = sum_2_prod
                                line.augmentation_transaction = sum_2_atran
                                line.diminution_cession = sum_2_cessi
                                line.diminution_withdrawal = sum_2_withd
                                line.diminution_transaction = sum_2_ctran
                                line.montant_start = sum_2_start
                                line.montant_end = sum_2_end
                            if asset.category_id.account_type in ['7','8','9','10','11','12','13'] and line.code =='333':
                                if asset.invoice_date.year == rec.fy_n_id.date_end.year:
                                    if asset.acquisition_mode == 'a':
                                        sum_3_acqui += asset.value
                                    elif asset.acquisition_mode == 'p':
                                        sum_3_prod += asset.value
                                    elif asset.acquisition_mode == 'v':
                                        sum_3_atran += asset.value
                                if asset.mode_session == 'c':
                                    sum_3_cessi += asset.value
                                elif asset.mode_session == 'r':
                                    sum_3_withd += asset.value
                                elif asset.mode_session == 'v':
                                    sum_3_ctran += asset.value
                                elif asset.invoice_date.year < rec.fy_n_id.date_end.year:
                                    sum_3_start += asset.value
                                sum_3_end = sum_3_start + (sum_3_acqui + sum_3_prod + sum_3_atran) - sum_3_cessi - sum_3_withd - sum_3_ctran
                                line.augmentation_acquisition = sum_3_acqui
                                line.augmentation_production = sum_3_prod
                                line.augmentation_transaction = sum_3_atran
                                line.diminution_cession = sum_3_cessi
                                line.diminution_withdrawal = sum_3_withd
                                line.diminution_transaction = sum_3_ctran
                                line.montant_start = sum_3_start
                                line.montant_end = sum_3_end
                            if asset.category_id.account_type in ['0','1','2','3','4','5','6','7','8','9','10','11','12','13'] and line.code =='444':
                                if asset.invoice_date.year == rec.fy_n_id.date_end.year:
                                    if asset.acquisition_mode == 'a':
                                        sum_4_acqui += asset.value
                                    elif asset.acquisition_mode == 'p':
                                        sum_4_prod += asset.value
                                    elif asset.acquisition_mode == 'v':
                                        sum_4_atran += asset.value
                                if asset.mode_session == 'c':
                                    sum_4_cessi += asset.value
                                elif asset.mode_session == 'r':
                                    sum_4_withd += asset.value
                                elif asset.mode_session == 'v':
                                    sum_4_ctran += asset.value
                                elif asset.invoice_date.year < rec.fy_n_id.date_end.year:
                                    sum_4_start += asset.value
                                sum_4_end = sum_4_start + (sum_4_acqui + sum_4_prod + sum_4_atran) - sum_4_cessi - sum_4_withd - sum_4_ctran
                                line.augmentation_acquisition = sum_4_acqui
                                line.augmentation_production = sum_4_prod
                                line.augmentation_transaction = sum_4_atran
                                line.diminution_cession = sum_4_cessi
                                line.diminution_withdrawal = sum_4_withd
                                line.diminution_transaction = sum_4_ctran
                                line.montant_start = sum_4_start
                                line.montant_end = sum_4_end

                            
    def get_lines(self):
        """This Function calculates Table 4 sub-Lines with its affectations"""
        for rec in self: 
            assets = self.env['account.asset.asset'].search([('id','!=',False),('company_id','=',self.env.company.id)])
            if rec.line_ids:
                for line in rec.line_ids:                    
                    sum_acqui = sum_prod = sum_atran  = sum_cessi = sum_withd = sum_ctran = sum_start = sum_end = 0
                    for asset in assets:
                        if not asset.date_cession or asset.date_cession.year > rec.fy_n_id.date_end.year:
                            if line.code == asset.category_id.account_type:
                                if asset.invoice_date.year == rec.fy_n_id.date_end.year:
                                    if asset.acquisition_mode == 'a':
                                        sum_acqui += asset.value
                                    elif asset.acquisition_mode == 'p':
                                        sum_prod += asset.value
                                    elif asset.acquisition_mode == 'v':
                                        sum_atran += asset.value
                                elif asset.invoice_date.year < rec.fy_n_id.date_end.year:
                                    sum_start += asset.value
                                sum_end = sum_start + (sum_acqui + sum_prod + sum_atran) - sum_cessi - sum_withd - sum_ctran
                            line.augmentation_acquisition = sum_acqui
                            line.augmentation_production = sum_prod
                            line.augmentation_transaction = sum_atran
                            line.diminution_cession = sum_cessi
                            line.diminution_withdrawal = sum_withd
                            line.diminution_transaction = sum_ctran
                            line.montant_start = sum_start
                            line.montant_end = sum_end
                        elif asset.date_cession.year == rec.fy_n_id.date_end.year:
                            if line.code == asset.category_id.account_type:
                                if asset.invoice_date.year == rec.fy_n_id.date_end.year:
                                    if asset.acquisition_mode == 'a':
                                        sum_acqui += asset.value
                                    elif asset.acquisition_mode == 'p':
                                        sum_prod += asset.value
                                    elif asset.acquisition_mode == 'v':
                                        sum_atran += asset.value
                                if asset.mode_session == 'c':
                                    sum_cessi += asset.value
                                elif asset.mode_session == 'r':
                                    sum_withd += asset.value
                                elif asset.mode_session == 'v':
                                    sum_ctran += asset.value
                                elif asset.invoice_date.year < rec.fy_n_id.date_end.year:
                                    sum_start += asset.value
                                sum_end = sum_start + (sum_acqui + sum_prod + sum_atran) - sum_cessi - sum_withd - sum_ctran
                            line.augmentation_acquisition = sum_acqui
                            line.augmentation_production = sum_prod
                            line.augmentation_transaction = sum_atran
                            line.diminution_cession = sum_cessi
                            line.diminution_withdrawal = sum_withd
                            line.diminution_transaction = sum_ctran
                            line.montant_start = sum_start
                            line.montant_end = sum_end
            rec.get_headers()
    
    def get_xml(self,parent):
        for rec in self:
            if rec.line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(11)# Special table id (read documentation)
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                val_1 = val_2 = val_3 = val_4 = val_5 = val_6 = val_7 = val_8 = 0
                for line in rec.line_ids:
                    val_1+=line.montant_start
                    val_2+=line.augmentation_acquisition
                    val_3+=line.augmentation_production
                    val_4+=line.augmentation_transaction
                    val_5+=line.diminution_cession
                    val_6+=line.diminution_withdrawal
                    val_7+=line.diminution_transaction
                    val_8+=line.montant_end
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_montant_start)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_start)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_augmentation_acquisition)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.augmentation_acquisition)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_augmentation_production)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.augmentation_production)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_augmentation_transaction)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.augmentation_transaction)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_diminution_cession)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.diminution_cession)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_diminution_withdrawal)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.diminution_withdrawal)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_diminution_transaction)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.diminution_transaction)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_montant_end)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_end)
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14045)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_1)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14046)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_2)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14047)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_3)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14048)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_4)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14049)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_5)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14050)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_6)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14051)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_7)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14052)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_8)
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
            else:
                pass
            
    def print_xlrd(self):
        data= {}
        return self.env.ref('immobilisation.action_immobilisation_xlsx_report').report_action(self, data=data)
    
class TableFourLines(models.Model):
    _name = 'immo.financiere.line'
    _description = 'immo.financiere.line'

    name = fields.Char(string=u"Lignes",required=True,readonly=True)
    code = fields.Char(string=u"Code", required=False,readonly=True )
    montant_start = fields.Float(string=u"DEBUT EXERCICE",  required=False,readonly=True )
    augmentation_acquisition = fields.Float(string=u"Acquisition",  required=False,readonly=True )
    augmentation_production = fields.Float(string=u"Production",  required=False, readonly=True)
    augmentation_transaction = fields.Float(string=u"Virement",  required=False,readonly=True )
    diminution_cession = fields.Float(string=u"Cession",  required=False,readonly=True )
    diminution_withdrawal = fields.Float(string=u"Retrait",  required=False,readonly=True )
    diminution_transaction = fields.Float(string=u"Virement",  required=False,readonly=True )
    montant_end = fields.Float(string=u"FIN EXERCICE",  required=False, readonly=True)

    # Code edi fields
    edi_montant_start = fields.Integer(string=u"EDI DEBUT EXERCICE",  required=False,readonly=True )
    edi_augmentation_acquisition = fields.Integer(string=u"EDI Acquisition",  required=False,readonly=True )
    edi_augmentation_production = fields.Integer(string=u"EDI Production",  required=False, readonly=True)
    edi_augmentation_transaction = fields.Integer(string=u"EDI Virement",  required=False,readonly=True )
    edi_diminution_cession = fields.Integer(string=u"EDI Cession",  required=False,readonly=True )
    edi_diminution_withdrawal = fields.Integer(string=u"EDI Retrait",  required=False,readonly=True )
    edi_diminution_transaction = fields.Integer(string=u"EDI Virement",  required=False,readonly=True )
    edi_montant_end = fields.Integer(string=u"EDI FIN EXERCICE",  required=False, readonly=True)
    
    # relational fields
    immo_id = fields.Many2one(comodel_name="immo.financiere", string="IMMOBILISATIONS AUTRES QUE FINANCIERES", required=False, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('immo.financiere.line'))

