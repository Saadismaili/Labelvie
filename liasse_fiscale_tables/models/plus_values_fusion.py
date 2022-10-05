# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)

class PlusValuesFusion(models.Model):
    _name = 'plus.values.fusion'
    _description = 'PLUS VALUES CONSTATEES EN CAS DE FUSION'

    name = fields.Char(string=u"Nom",default="ETAT DES PLUS-VALUES CONSTATEES EN CAS DE FUSION",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    plus_values_fusion_line_ids = fields.One2many(comodel_name="plus.values.fusion.line", inverse_name="plus_values_fusion_id", string="Lignes", required=False, copy=True, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('plus.values.fusion'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]

    @api.model
    def create(self, values):
        return super(PlusValuesFusion,self).create({
            'plus_values_fusion_line_ids' : self.env['plus.values.fusion.line'].create([{'name':"1- Terrains (1)",'edi_valeur_apport':1110,'edi_valeur_nette_comptable':1111,'edi_plus_value_constatee':1112,'edi_fraction_exercice_ant':1113,'edi_fraction_exercice_actuel':1114,'edi_cumul_plus_value_rapportee':1115,'edi_solde_plus_value_non_rapportee':1116,'edi_observations':1117,'plus_values_fusion_id':self.id,},
                                                                              {'name':"2- Constructions",'edi_valeur_apport':1119,'edi_valeur_nette_comptable':1120,'edi_plus_value_constatee':1121,'edi_fraction_exercice_ant':1122,'edi_fraction_exercice_actuel':1123,'edi_cumul_plus_value_rapportee':1124,'edi_solde_plus_value_non_rapportee':1125,'edi_observations':1126,'plus_values_fusion_id':self.id,},
                                                                              {'name':"3- Matériel et outillage",'edi_valeur_apport':1128,'edi_valeur_nette_comptable':1129,'edi_plus_value_constatee':1130,'edi_fraction_exercice_ant':1131,'edi_fraction_exercice_actuel':1132,'edi_cumul_plus_value_rapportee':1133,'edi_solde_plus_value_non_rapportee':1134,'edi_observations':1135,'plus_values_fusion_id':self.id,},
                                                                              {'name':"4- Matériel de transport",'edi_valeur_apport':1137,'edi_valeur_nette_comptable':1138,'edi_plus_value_constatee':1139,'edi_fraction_exercice_ant':1140,'edi_fraction_exercice_actuel':1141,'edi_cumul_plus_value_rapportee':1142,'edi_solde_plus_value_non_rapportee':1143,'edi_observations':1144,'plus_values_fusion_id':self.id,},
                                                                              {'name':"5- Agencements - installations",'edi_valeur_apport':1146,'edi_valeur_nette_comptable':1147,'edi_plus_value_constatee':1148,'edi_fraction_exercice_ant':1149,'edi_fraction_exercice_actuel':1150,'edi_cumul_plus_value_rapportee':1151,'edi_solde_plus_value_non_rapportee':1152,'edi_observations':1153,'plus_values_fusion_id':self.id,},
                                                                              {'name':"6- Brevets",'edi_valeur_apport':1155,'edi_valeur_nette_comptable':1156,'edi_plus_value_constatee':1157,'edi_fraction_exercice_ant':1158,'edi_fraction_exercice_actuel':1159,'edi_cumul_plus_value_rapportee':1160,'edi_solde_plus_value_non_rapportee':1161,'edi_observations':1162,'plus_values_fusion_id':self.id,},
                                                                              {'name':"7- Autres éléments amortissables",'edi_valeur_apport':1164,'edi_valeur_nette_comptable':1165,'edi_plus_value_constatee':1166,'edi_fraction_exercice_ant':1167,'edi_fraction_exercice_actuel':1168,'edi_cumul_plus_value_rapportee':1169,'edi_solde_plus_value_non_rapportee':1170,'edi_observations':1171,'plus_values_fusion_id':self.id,},
                                                                              {'name':"8- Titres de participation",'edi_valeur_apport':1173,'edi_valeur_nette_comptable':1174,'edi_plus_value_constatee':1175,'edi_fraction_exercice_ant':1176,'edi_fraction_exercice_actuel':1177,'edi_cumul_plus_value_rapportee':1178,'edi_solde_plus_value_non_rapportee':1179,'edi_observations':1180,'plus_values_fusion_id':self.id,},
                                                                              {'name':"9- Fonds de commerce",'edi_valeur_apport':1182,'edi_valeur_nette_comptable':1183,'edi_plus_value_constatee':1184,'edi_fraction_exercice_ant':1185,'edi_fraction_exercice_actuel':1186,'edi_cumul_plus_value_rapportee':1187,'edi_solde_plus_value_non_rapportee':1188,'edi_observations':1189,'plus_values_fusion_id':self.id,},
                                                                              {'name':"10- Autres éléments non amortissables",'edi_valeur_apport':1191,'edi_valeur_nette_comptable':1192,'edi_plus_value_constatee':1193,'edi_fraction_exercice_ant':1194,'edi_fraction_exercice_actuel':1195,'edi_cumul_plus_value_rapportee':1196,'edi_solde_plus_value_non_rapportee':1197,'edi_observations':1198,'plus_values_fusion_id':self.id,},
                                                            ]),})
    # This Function even that its returns nothing but it will be called in another model please refer to pdf generator (module:osi_generate_me)
    def get_lines(self):
        pass
    
    def get_xml(self,parent):
        for rec in self:
            if rec.plus_values_fusion_line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(26)
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                val_1 = val_2 = val_3 = val_4 = val_5 = val_6 = val_7 = 0
                for line in rec.plus_values_fusion_line_ids:
                    val_1 += line.valeur_apport
                    val_2 += line.valeur_nette_comptable
                    val_3 += line.plus_value_constatee
                    val_4 += line.fraction_exercice_ant
                    val_5 += line.fraction_exercice_actuel
                    val_6 += line.cumul_plus_value_rapportee
                    val_7 += line.solde_plus_value_non_rapportee
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_valeur_apport)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.valeur_apport)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_valeur_nette_comptable)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.valeur_nette_comptable)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_plus_value_constatee)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.plus_value_constatee)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_fraction_exercice_ant)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.fraction_exercice_ant)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_fraction_exercice_actuel)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.fraction_exercice_actuel)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_cumul_plus_value_rapportee)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.cumul_plus_value_rapportee)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_solde_plus_value_non_rapportee)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.solde_plus_value_non_rapportee)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_observations)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.observations)
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1200)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_1)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1201)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_2)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1202)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_3)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1203)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_4)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1204)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_5)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1205)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_6)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(1206)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_7) 
                   
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
                extra_field_valeur = etree.SubElement(extra_field_valeurs, "ExtraFieldValeur")
                extra_field = etree.SubElement(extra_field_valeur, "extraField")
                etree.SubElement(extra_field,"code").text = str(54)
                etree.SubElement(extra_field_valeur,"valeur").text = str(rec.fy_n_id.date_end)
            else:
                pass
class PlusValuesFusionLine(models.Model):
    _name = 'plus.values.fusion.line'
    _description = 'LIGNES PLUS VALUES CONSTATEES EN CAS DE FUSION'

    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('plus.values.fusion.line'))
    name = fields.Char(string=u"Eléments",required=True,)
    code = fields.Char(string=u"Code", required=False, )
    valeur_apport = fields.Float(string=u"Valeur d'apport", required=False, )
    valeur_nette_comptable = fields.Float(string=u"Valeur nette comptable",  required=False, )
    plus_value_constatee = fields.Float(string=u"Plus-value constatée et différée",  required=False, )
    fraction_exercice_ant = fields.Float(string=u"Fraction de la plus-value rapportée aux exercices antérieurs(cumul)",  required=False, )
    fraction_exercice_actuel = fields.Float(string=u"Fraction de la plus-value rapportée à l'exercice actuel",  required=False, )
    cumul_plus_value_rapportee = fields.Float(string=u"Cumul des plus-value rapportées",  required=False, )
    solde_plus_value_non_rapportee = fields.Float(string=u"Solde des plus-values non-imputées",  required=False, )
    observations = fields.Text(string="Observations", required=False, )
    plus_values_fusion_id = fields.Many2one(comodel_name="plus.values.fusion", string="PLUS-VALUES CONSTATEES EN CAS DE FUSION", required=False, )
    
    # Code edi
    
    edi_valeur_apport = fields.Integer(string=u"Valeur d'apport", required=False, )
    edi_valeur_nette_comptable = fields.Integer(string=u"Valeur nette comptable",  required=False, )
    edi_plus_value_constatee = fields.Integer(string=u"Plus-value constatée et différée",  required=False, )
    edi_fraction_exercice_ant = fields.Integer(string=u"Fraction de la plus-value rapportée aux exercices antérieurs(cumul)",  required=False, )
    edi_fraction_exercice_actuel = fields.Integer(string=u"Fraction de la plus-value rapportée à l'exercice actuel",  required=False, )
    edi_cumul_plus_value_rapportee = fields.Integer(string=u"Cumul des plus-value rapportées",  required=False, )
    edi_solde_plus_value_non_rapportee = fields.Integer(string=u"Solde des plus-values non-imputées",  required=False, )
    edi_observations = fields.Integer(string="Observations", required=False, )
    
    