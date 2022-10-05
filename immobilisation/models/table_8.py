# -*- coding: utf-8 -*-

from odoo import models, fields, api

from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)

class TableHeight(models.Model):
    _name = 'immo.amortissements'
    _description = 'TABLEAU DES AMORTISSEMENTS'

    name = fields.Char(string=u"Nom",default="AMORTISSEMENTS",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False,store=True,)
    line_ids = fields.One2many(string='Lignes',comodel_name='immo.amortissements.line',inverse_name='immo_id' )
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('immo.amortissements'))

    

    @api.model
    def create(self, values):
        return super(TableHeight,self).create({
            'line_ids' : self.env['immo.amortissements.line'].create([{'name':'IMMOBILISATION EN NON-VALEURS','edi_debut_exercice':1231,'edi_dotation_exercice':1232,'edi_amortissement_sortie':1233,'edi_cumule_amortissement':1234,'code':'111','immo_id':self.id,},
                                                                  {'name':'* Frais préliminaires','edi_debut_exercice':1236,'edi_dotation_exercice':1237,'edi_amortissement_sortie':1238,'edi_cumule_amortissement':1239,'code':'1','immo_id':self.id,},
                                                                  {'name':'* Charges à répartir sur plusieurs exercices','edi_debut_exercice':1241,'edi_dotation_exercice':1242,'edi_amortissement_sortie':1243,'edi_cumule_amortissement':1244,'code':'2','immo_id':self.id,},
                                                                  {'name':'* Primes des rembourssement des obligations','edi_debut_exercice':1246,'edi_dotation_exercice':1247,'edi_amortissement_sortie':1248,'edi_cumule_amortissement':1249,'code':'0','immo_id':self.id,},
                                                                  {'name':'IMMOBILISATIONS INCORPORELLES','edi_debut_exercice':1624,'edi_dotation_exercice':1629,'edi_amortissement_sortie':1650,'edi_cumule_amortissement':1679,'code':'222','immo_id':self.id,},
                                                                  {'name':'* Immobilisation en recherche et développement +','edi_debut_exercice':1625,'edi_dotation_exercice':1630,'edi_amortissement_sortie':1651,'edi_cumule_amortissement':1680,'code':'3','immo_id':self.id,},
                                                                  {'name':'* Brevets, marques droits et valeurs similairest','edi_debut_exercice':1626,'edi_dotation_exercice':1631,'edi_amortissement_sortie':1652,'edi_cumule_amortissement':1681,'code':'4','immo_id':self.id,},
                                                                  {'name':'* Fonds commercial','code':'5','edi_debut_exercice':1627,'edi_dotation_exercice':1632,'edi_amortissement_sortie':1653,'edi_cumule_amortissement':1682,'immo_id':self.id,},
                                                                  {'name':'* Autres immobilisations incorporelles','code':'6','edi_debut_exercice':1628,'edi_dotation_exercice':1633,'edi_amortissement_sortie':1654,'edi_cumule_amortissement':1683,'immo_id':self.id,},
                                                                  {'name':'IMMOBILISATIONS CORPORELLES','code':'333','edi_debut_exercice':1700,'edi_dotation_exercice':1708,'edi_amortissement_sortie':1716,'edi_cumule_amortissement':1724,'immo_id':self.id,},
                                                                  {'name':'* Terrains','code':'7','edi_debut_exercice':1701,'edi_dotation_exercice':1709,'edi_amortissement_sortie':1717,'edi_cumule_amortissement':1725,'immo_id':self.id,},
                                                                  {'name':'* Constructions','code':'8','immo_id':self.id,'edi_debut_exercice':1702,'edi_dotation_exercice':1710,'edi_amortissement_sortie':1718,'edi_cumule_amortissement':1726,},
                                                                  {'name':'* Installations techniques; matériel et outillage','code':'9','edi_debut_exercice':1703,'edi_dotation_exercice':1711,'edi_amortissement_sortie':1719,'edi_cumule_amortissement':1727,'immo_id':self.id,},
                                                                  {'name':'* Matériel de transport','code':'10','edi_debut_exercice':1704,'edi_dotation_exercice':1712,'edi_amortissement_sortie':1720,'edi_cumule_amortissement':1728,'immo_id':self.id,},
                                                                  {'name':'* Mobilier, matériel de bureau et aménagements','edi_debut_exercice':1705,'edi_dotation_exercice':1713,'edi_amortissement_sortie':1721,'edi_cumule_amortissement':1729,'code':'11','immo_id':self.id,},
                                                                  {'name':'* Autres immobilisations corporelles','code':'12','edi_debut_exercice':1706,'edi_dotation_exercice':1714,'edi_amortissement_sortie':1722,'edi_cumule_amortissement':1730,'immo_id':self.id,},
                                                                  {'name':'* Immobilisations corporelles en cours','code':'13','edi_debut_exercice':1707,'edi_dotation_exercice':1715,'edi_amortissement_sortie':1723,'edi_cumule_amortissement':1731,'immo_id':self.id,},
                                                                  {'name':'TOTAL GENERAL',  'code':'444','immo_id':self.id,}]),})

    def get_headers(self):
        """This Function calculates Table 8 head-Lines with its affectations"""
        for rec in self:
            assets = self.env['account.asset.asset'].search([('id','!=',False),('company_id','=',self.env.company.id)])
            if rec.line_ids:
                for line in rec.line_ids:                    
                    sum_1_out = sum_1_end = sum_1_start  = sum_1_depreciated = 0
                    sum_2_out = sum_2_end = sum_2_start  = sum_2_depreciated = 0
                    sum_3_out = sum_3_end = sum_3_start  = sum_3_depreciated = 0
                    sum_4_out = sum_4_end = sum_4_start  = sum_4_depreciated = 0
                    for asset in assets:
                        if not asset.date_cession or asset.date_cession.year > rec.fy_n_id.date_end.year:
                            if line.code == '111' and asset.category_id.account_type in ['0','1','2']:
                                if asset.depreciation_line_ids:
                                    for depreciation in asset.depreciation_line_ids:
                                        if depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                            sum_1_depreciated += depreciation.amount
                                        elif depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                            sum_1_start += depreciation.amount
                                        if asset.cession_price_ht > 0.0:
                                            sum_1_out = sum_1_depreciated + sum_1_start
                                        sum_1_end = sum_1_depreciated + sum_1_start - sum_1_out
                                line.debut_exercice = sum_1_start
                                line.dotation_exercice = sum_1_depreciated
                                line.amortissement_sortie = sum_1_out
                                line.cumule_amortissement = sum_1_end
                            elif line.code == '222' and asset.category_id.account_type in ['3','4','5','6']:
                                if asset.depreciation_line_ids:
                                    for depreciation in asset.depreciation_line_ids:
                                        if depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                            sum_2_depreciated += depreciation.amount
                                        elif depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                            sum_2_start += depreciation.amount
                                        if asset.cession_price_ht > 0.0:
                                            sum_2_out = sum_2_depreciated + sum_2_start
                                        sum_2_end = sum_2_depreciated + sum_2_start - sum_2_out
                                line.debut_exercice = sum_2_start
                                line.dotation_exercice = sum_2_depreciated
                                line.amortissement_sortie = sum_2_out
                                line.cumule_amortissement = sum_2_end
                            elif line.code == '333' and asset.category_id.account_type in ['7','8','9','10','11','12','13']:
                                if asset.depreciation_line_ids:
                                    for depreciation in asset.depreciation_line_ids:
                                        if depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                            sum_3_depreciated += depreciation.amount
                                        elif depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                            sum_3_start += depreciation.amount
                                        if asset.cession_price_ht > 0.0:
                                            sum_3_out = sum_3_depreciated + sum_3_start
                                        sum_3_end = sum_3_depreciated + sum_3_start - sum_3_out
                                line.debut_exercice = sum_3_start
                                line.dotation_exercice = sum_3_depreciated
                                line.amortissement_sortie = sum_3_out
                                line.cumule_amortissement = sum_3_end
                            elif line.code == '444' and asset.category_id.account_type in ['0','1','2','3','4','5','6','7','8','9','10','11','12','13']:
                                if asset.depreciation_line_ids:
                                    for depreciation in asset.depreciation_line_ids:
                                        if depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                            sum_4_depreciated += depreciation.amount
                                        elif depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                            sum_4_start += depreciation.amount
                                        if asset.cession_price_ht > 0.0:
                                            sum_4_out = sum_4_depreciated + sum_4_start
                                        sum_4_end = sum_4_depreciated + sum_4_start - sum_4_out
                                line.debut_exercice = sum_4_start
                                line.dotation_exercice = sum_4_depreciated
                                line.amortissement_sortie = sum_4_out
                                line.cumule_amortissement = sum_4_end
                        elif asset.date_cession.year == rec.fy_n_id.date_end.year:
                            if line.code == '111' and asset.category_id.account_type in ['0','1','2']:
                                if asset.depreciation_line_ids:
                                    for depreciation in asset.depreciation_line_ids:
                                        if depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                            sum_1_depreciated += depreciation.amount
                                        elif depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                            sum_1_start += depreciation.amount
                                        if asset.cession_price_ht > 0.0 or asset.cession_price_ttc > 0.0 or asset.amount_vna > 0.0 or asset.sold_amount > 0.0:
                                            sum_1_out = sum_1_depreciated + sum_1_start
                                        sum_1_end = sum_1_depreciated + sum_1_start - sum_1_out
                                line.debut_exercice = sum_1_start
                                line.dotation_exercice = sum_1_depreciated
                                line.amortissement_sortie = sum_1_out
                                line.cumule_amortissement = sum_1_end
                            elif line.code == '222' and asset.category_id.account_type in ['3','4','5','6']:
                                if asset.depreciation_line_ids:
                                    for depreciation in asset.depreciation_line_ids:
                                        if depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                            sum_2_depreciated += depreciation.amount
                                        elif depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                            sum_2_start += depreciation.amount
                                        if asset.cession_price_ht > 0.0 or asset.cession_price_ttc > 0.0 or asset.amount_vna > 0.0 or asset.sold_amount > 0.0:
                                            sum_2_out = sum_2_depreciated + sum_2_start
                                        sum_2_end = sum_2_depreciated + sum_2_start - sum_2_out
                                line.debut_exercice = sum_2_start
                                line.dotation_exercice = sum_2_depreciated
                                line.amortissement_sortie = sum_2_out
                                line.cumule_amortissement = sum_2_end
                            elif line.code == '333' and asset.category_id.account_type in ['7','8','9','10','11','12','13']:
                                if asset.depreciation_line_ids:
                                    for depreciation in asset.depreciation_line_ids:
                                        if depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                            sum_3_depreciated += depreciation.amount
                                        elif depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                            sum_3_start += depreciation.amount
                                        if asset.cession_price_ht > 0.0 or asset.cession_price_ttc > 0.0 or asset.amount_vna > 0.0 or asset.sold_amount > 0.0: 
                                            sum_3_out = sum_3_depreciated + sum_3_start
                                        sum_3_end = sum_3_depreciated + sum_3_start - sum_3_out
                                line.debut_exercice = sum_3_start
                                line.dotation_exercice = sum_3_depreciated
                                line.amortissement_sortie = sum_3_out
                                line.cumule_amortissement = sum_3_end
                            elif line.code == '444' and asset.category_id.account_type in ['0','1','2','3','4','5','6','7','8','9','10','11','12','13']:
                                if asset.depreciation_line_ids:
                                    for depreciation in asset.depreciation_line_ids:
                                        if depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                            sum_4_depreciated += depreciation.amount
                                        elif depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                            sum_4_start += depreciation.amount
                                        if asset.cession_price_ht > 0.0 or asset.cession_price_ttc > 0.0 or asset.amount_vna > 0.0 or asset.sold_amount > 0.0: 
                                            sum_4_out = sum_4_depreciated + sum_4_start
                                        sum_4_end = sum_4_depreciated + sum_4_start - sum_4_out
                                line.debut_exercice = sum_4_start
                                line.dotation_exercice = sum_4_depreciated
                                line.amortissement_sortie = sum_4_out
                                line.cumule_amortissement = sum_4_end
                                    
    def get_lines(self):
            """This Function calculates Table 8 sub-Lines with its affectations"""
            for rec in self:
                assets = self.env['account.asset.asset'].search([('id','!=',False),('company_id','=',self.env.company.id)])
                if rec.line_ids:
                    for line in rec.line_ids:                    
                        sum_out = sum_end = sum_start  = sum_depreciated = 0
                        for asset in assets:
                            if not asset.date_cession or asset.date_cession.year > rec.fy_n_id.date_end.year:
                                if line.code == asset.category_id.account_type:
                                    if asset.depreciation_line_ids:
                                        for depreciation in asset.depreciation_line_ids:
                                            if depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                                sum_depreciated += depreciation.amount
                                            elif depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                                sum_start += depreciation.amount
                            elif asset.date_cession.year == rec.fy_n_id.date_end.year:
                                if line.code == asset.category_id.account_type:
                                    if asset.depreciation_line_ids:
                                        for depreciation in asset.depreciation_line_ids:
                                            if depreciation.depreciation_date.year == rec.fy_n_id.date_end.year:
                                                sum_depreciated += depreciation.amount
                                            elif depreciation.depreciation_date.year < rec.fy_n_id.date_end.year:
                                                sum_start += depreciation.amount
                            if asset.cession_price_ht > 0.0:
                                sum_out = sum_depreciated + sum_start
                            sum_end = sum_depreciated + sum_start - sum_out
                        line.debut_exercice = sum_start
                        line.dotation_exercice = sum_depreciated
                        line.amortissement_sortie = sum_out
                        line.cumule_amortissement = sum_end
                rec.get_headers()

    def get_xml(self,parent):
        for rec in self:
            if rec.line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(24) # read documentation XML
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                val_1 = val_2 = val_3 = val_4 = 0
                for line in rec.line_ids:
                    val_1+=line.debut_exercice
                    val_2+=line.dotation_exercice
                    val_3+=line.amortissement_sortie
                    val_4+=line.cumule_amortissement
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_debut_exercice)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.debut_exercice)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_dotation_exercice)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.dotation_exercice)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_amortissement_sortie)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.amortissement_sortie)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_cumule_amortissement)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.cumule_amortissement)
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14061)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_1)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14062)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_2)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14063)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_3)
                
                valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                cellule = etree.SubElement(valeur_cellule, "cellule")
                etree.SubElement(cellule, "codeEdi").text = str(14064)
                etree.SubElement(valeur_cellule, "valeur").text = str(val_4)
                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")
            else:
                pass
                                       
class TableHeightLines(models.Model):
    _name = 'immo.amortissements.line'
    _description = 'TABLEAU DES AMORTISSEMENTS LIGNES'

    name = fields.Char(string=u"Nature",required=True,readonly=True)
    code = fields.Char(string=u"Code", required=False, readonly=True)
    debut_exercice = fields.Float(string=u"DEBUT EXERCICE",  required=False, readonly=True)
    dotation_exercice = fields.Float(string=u"Dotation Exercice",  required=False,readonly=True )
    amortissement_sortie = fields.Float(string=u"Amortissements sur immobilis-sorties",  required=False,readonly=True )
    cumule_amortissement = fields.Float(string=u"Cumul d'amortissement fin exercice",  required=False, readonly=True)
    
    # Code Edi
    edi_debut_exercice = fields.Integer(string=u"DEBUT EXERCICE",  required=False, readonly=True)
    edi_dotation_exercice = fields.Integer(string=u"Dotation Exercice",  required=False,readonly=True )
    edi_amortissement_sortie = fields.Integer(string=u"Amortissements sur immobilis-sorties",  required=False,readonly=True )
    edi_cumule_amortissement = fields.Integer(string=u"Cumul d'amortissement fin exercice",  required=False, readonly=True)
    
    # Rrelational Fields
    immo_id = fields.Many2one(comodel_name="immo.amortissements", string="AMORTISSEMENTS", required=False,readonly=True )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('immo.amortissements.line'))
