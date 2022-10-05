# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)

class DetailStock(models.Model):
    _name = 'detail.stock'
    _description = 'Detail Stock'

    name = fields.Char(string=u"Nom",default="ETAT DETAIL DES STOCKS",required=True,)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    detail_stock_line_ids = fields.One2many(comodel_name="detail.stock.line", inverse_name="detail_stock_id", string="Lignes", required=False, copy=True, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('detail.stock'))
    _sql_constraints = [
        ('unique_fy', 'UNIQUE(fy_n_id)', 'Un autre tableau existe pour le meme exercice!'),
    ]
            
    @api.model
    def create(self, values):
        return super(DetailStock,self).create({
            'fy_n_id':self.fy_n_id.id,
            'detail_stock_line_ids' : self.env['detail.stock.line'].create([{'name':'I.STOCKS APPROVISIONNEMENT','edi_montant_brut_stock_final':1401,'edi_provisions_stock_final':1402,'edi_montant_net_stock_final':1403,'edi_montant_brut_stock_initial':1404,'edi_provisions_stock_initial':1405,'edi_montant_net_stock_initial':1406,'edi_variation_stock':1407,'detail_stock_id':self.id,},
                                                                  {'name':'- Biens & Produits Destinés à la Revente en l\'état','edi_montant_brut_stock_final':1410,'edi_provisions_stock_final':1410,'edi_montant_net_stock_final':1411,'edi_montant_brut_stock_initial':1412,'edi_provisions_stock_initial':1413,'edi_montant_net_stock_initial':1414,'edi_variation_stock':1415,'detail_stock_id':self.id,},
                                                                  {'name':'* Biens Immeubles','edi_montant_brut_stock_final':1417,'edi_provisions_stock_final':1418,'edi_montant_net_stock_final':1419,'edi_montant_brut_stock_initial':1420,'edi_provisions_stock_initial':1421,'edi_montant_net_stock_initial':1422,'edi_variation_stock':1423,'detail_stock_id':self.id,},
                                                                  {'name':'* Biens Meubles','edi_montant_brut_stock_final':1425,'edi_provisions_stock_final':1426,'edi_montant_net_stock_final':1427,'edi_montant_brut_stock_initial':1428,'edi_provisions_stock_initial':1429,'edi_montant_net_stock_initial':1430,'edi_variation_stock':1431,'detail_stock_id':self.id,},
                                                                  {'name':'- Biens & Matière Premières Destinés aux activités de Production & de Transformation','edi_montant_brut_stock_final':1433,'edi_provisions_stock_final':1434,'edi_montant_net_stock_final':1435,'edi_montant_brut_stock_initial':1436,'edi_provisions_stock_initial':1437,'edi_montant_net_stock_initial':1438,'edi_variation_stock':1439,'detail_stock_id':self.id,},
                                                                  {'name':'* Matière Premières','detail_stock_id':self.id,'edi_montant_brut_stock_final':1449,'edi_provisions_stock_final':1450,'edi_montant_net_stock_final':1451,'edi_montant_brut_stock_initial':1452,'edi_provisions_stock_initial':1453,'edi_montant_net_stock_initial':1454,'edi_variation_stock':1455,},
                                                                  {'name':'* Matières Consommables','detail_stock_id':self.id,'edi_montant_brut_stock_final':1457,'edi_provisions_stock_final':1458,'edi_montant_net_stock_final':1459,'edi_montant_brut_stock_initial':1460,'edi_provisions_stock_initial':1461,'edi_montant_net_stock_initial':1462,'edi_variation_stock':1463,},
                                                                  {'name':'* Pièces Détachées','detail_stock_id':self.id,'edi_montant_brut_stock_final':1465,'edi_provisions_stock_final':1466,'edi_montant_net_stock_final':1467,'edi_montant_brut_stock_initial':1468,'edi_provisions_stock_initial':1469,'edi_montant_net_stock_initial':1470,'edi_variation_stock':1471,},
                                                                  {'name':'* Carburants, Lubrifiants Pour Véhicules de transport','edi_montant_brut_stock_final':1473,'edi_provisions_stock_final':1474,'edi_montant_net_stock_final':1475,'edi_montant_brut_stock_initial':1476,'edi_provisions_stock_initial':1477,'edi_montant_net_stock_initial':1478,'edi_variation_stock':1479,'detail_stock_id':self.id,},
                                                                  {'name':'- Emballage','detail_stock_id':self.id,'edi_montant_brut_stock_final':1481,'edi_provisions_stock_final':1482,'edi_montant_net_stock_final':1483,'edi_montant_brut_stock_initial':1484,'edi_provisions_stock_initial':1485,'edi_montant_net_stock_initial':1486,'edi_variation_stock':1487,},
                                                                  {'name':'* Récupérables','detail_stock_id':self.id,'edi_montant_brut_stock_final':1555,'edi_provisions_stock_final':1556,'edi_montant_net_stock_final':1557,'edi_montant_brut_stock_initial':1558,'edi_provisions_stock_initial':1559,'edi_montant_net_stock_initial':1560,'edi_variation_stock':1561,},
                                                                  {'name':'* Vendus','detail_stock_id':self.id,'edi_montant_brut_stock_final':1596,'edi_provisions_stock_final':1597,'edi_montant_net_stock_final':1598,'edi_montant_brut_stock_initial':1599,'edi_provisions_stock_initial':1600,'edi_montant_net_stock_initial':1601,'edi_variation_stock':1602,},
                                                                  {'name':'* Perdus','detail_stock_id':self.id,'edi_montant_brut_stock_final':1604,'edi_provisions_stock_final':1605,'edi_montant_net_stock_final':1606,'edi_montant_brut_stock_initial':1607,'edi_provisions_stock_initial':1608,'edi_montant_net_stock_initial':1609,'edi_variation_stock':1610,},
                                                                  {'name':'TOTAL STOCKS APPROVISIONNEMENT','detail_stock_id':self.id,'edi_montant_brut_stock_final':1612,'edi_provisions_stock_final':1613,'edi_montant_net_stock_final':1614,'edi_montant_brut_stock_initial':1615,'edi_provisions_stock_initial':1616,'edi_montant_net_stock_initial':1617,'edi_variation_stock':1618,},
                                                                  {'name':'II.STOCK EN-COURS PRODUCTION DE BIENS & SERVICE','edi_montant_brut_stock_final':1635,'edi_provisions_stock_final':1636,'edi_montant_net_stock_final':1637,'edi_montant_brut_stock_initial':1638,'edi_provisions_stock_initial':1639,'edi_montant_net_stock_initial':1640,'edi_variation_stock':1641,'detail_stock_id':self.id,},
                                                                  {'name':'* Produits En cours','detail_stock_id':self.id,'edi_montant_brut_stock_final':1643,'edi_provisions_stock_final':1644,'edi_montant_net_stock_final':1645,'edi_montant_brut_stock_initial':1646,'edi_provisions_stock_initial':1647,'edi_montant_net_stock_initial':1648,'edi_variation_stock':1649,},
                                                                  {'name':'* Etudes En cours','detail_stock_id':self.id,'edi_montant_brut_stock_final':1656,'edi_provisions_stock_final':1657,'edi_montant_net_stock_final':1658,'edi_montant_brut_stock_initial':1659,'edi_provisions_stock_initial':1660,'edi_montant_net_stock_initial':1661,'edi_variation_stock':1662,},
                                                                  {'name':'* Travaux En-cours','detail_stock_id':self.id,'edi_montant_brut_stock_final':1664,'edi_provisions_stock_final':1665,'edi_montant_net_stock_final':1666,'edi_montant_brut_stock_initial':1667,'edi_provisions_stock_initial':1668,'edi_montant_net_stock_initial':1669,'edi_variation_stock':1670,},
                                                                  {'name':'* Services En-cours','detail_stock_id':self.id,'edi_montant_brut_stock_final':1672,'edi_provisions_stock_final':1673,'edi_montant_net_stock_final':1674,'edi_montant_brut_stock_initial':1675,'edi_provisions_stock_initial':1676,'edi_montant_net_stock_initial':1677,'edi_variation_stock':1678,},
                                                                  {'name':'TOTAL STOCKS DES EN-COURS','detail_stock_id':self.id,'edi_montant_brut_stock_final':1685,'edi_provisions_stock_final':1686,'edi_montant_net_stock_final':1687,'edi_montant_brut_stock_initial':1688,'edi_provisions_stock_initial':1689,'edi_montant_net_stock_initial':1690,'edi_variation_stock':1691,},
                                                                  {'name':'III.STOCK PRODUITS FINIS','detail_stock_id':self.id,'edi_montant_brut_stock_final':1736,'edi_provisions_stock_final':1737,'edi_montant_net_stock_final':1738,'edi_montant_brut_stock_initial':1739,'edi_provisions_stock_initial':1740,'edi_montant_net_stock_initial':1741,'edi_variation_stock':1742,},
                                                                  {'name':'* Produits Finis','detail_stock_id':self.id,'edi_montant_brut_stock_final':1757,'edi_provisions_stock_final':1758,'edi_montant_net_stock_final':1759,'edi_montant_brut_stock_initial':1760,'edi_provisions_stock_initial':1761,'edi_montant_net_stock_initial':1762,'edi_variation_stock':1763,},
                                                                  {'name':'* Biens Finis','detail_stock_id':self.id,'edi_montant_brut_stock_final':1769,'edi_provisions_stock_final':1770,'edi_montant_net_stock_final':1771,'edi_montant_brut_stock_initial':1772,'edi_provisions_stock_initial':1773,'edi_montant_net_stock_initial':1774,'edi_variation_stock':1775,},
                                                                  {'name':'TOTAL STOCKS PRODUITS & BIENS FINIS','detail_stock_id':self.id,'edi_montant_brut_stock_final':1800,'edi_provisions_stock_final':1801,'edi_montant_net_stock_final':1802,'edi_montant_brut_stock_initial':1803,'edi_provisions_stock_initial':1804,'edi_montant_net_stock_initial':1805,'edi_variation_stock':1806,},
                                                                  {'name':'IV.STOCK PRODUITS RESIDUELS','detail_stock_id':self.id,'edi_montant_brut_stock_final':1819,'edi_provisions_stock_final':1820,'edi_montant_net_stock_final':1821,'edi_montant_brut_stock_initial':1822,'edi_provisions_stock_initial':1823,'edi_montant_net_stock_initial':1824,'edi_variation_stock':1825,},
                                                                  {'name':'* Déchets','detail_stock_id':self.id,'edi_montant_brut_stock_final':1836,'edi_provisions_stock_final':1837,'edi_montant_net_stock_final':1838,'edi_montant_brut_stock_initial':1839,'edi_provisions_stock_initial':1840,'edi_montant_net_stock_initial':1841,'edi_variation_stock':1842,},
                                                                  {'name':'* Rebuts','detail_stock_id':self.id,'edi_montant_brut_stock_final':1853,'edi_provisions_stock_final':1854,'edi_montant_net_stock_final':1855,'edi_montant_brut_stock_initial':1856,'edi_provisions_stock_initial':1857,'edi_montant_net_stock_initial':1858,'edi_variation_stock':1859,},
                                                                  {'name':'* Matières de Récupération','detail_stock_id':self.id,'edi_montant_brut_stock_final':1861,'edi_provisions_stock_final':1862,'edi_montant_net_stock_final':1863,'edi_montant_brut_stock_initial':1864,'edi_provisions_stock_initial':1865,'edi_montant_net_stock_initial':1866,'edi_variation_stock':1867,},
                                                                  {'name':'TOTAL STOCKS PRODUITS RESIDUELS','detail_stock_id':self.id,'edi_montant_brut_stock_final':1869,'edi_provisions_stock_final':1870,'edi_montant_net_stock_final':1871,'edi_montant_brut_stock_initial':1872,'edi_provisions_stock_initial':1873,'edi_montant_net_stock_initial':1874,'edi_variation_stock':1875,},
                                                                  {'name':'TOTAL  GENERAL','detail_stock_id':self.id,'edi_montant_brut_stock_final':1886,'edi_provisions_stock_final':1887,'edi_montant_net_stock_final':1888,'edi_montant_brut_stock_initial':1889,'edi_provisions_stock_initial':1890,'edi_montant_net_stock_initial':1891,'edi_variation_stock':1892,}]),})

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
        elif len(list1) == 6:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2] and list1[3] == list2[3] and list1[4] == list2[4] and list1[5] == list2[5]:
                return True
        elif len(list1) == 7:
            if list1[0] == list2[0] and list1[1] == list2[1] and list1[2] == list2[2] and list1[3] == list2[3] and list1[4] == list2[4] and list1[5] == list2[5] and list1[6] == list2[6]:
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
        
    
    def get_lines(self):
        for rec in self:
            line_1 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Biens Immeubles')])
            line_1.write({
                'montant_brut_stock_final':abs(self.bal_calulator_current_year(['3111','3116'])),
                'provisions_stock_final' :abs(self.bal_calulator_current_year(['39111','39116'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39111%'),('code','=like','39116%')]).exists() else abs(self.bal_calulator_current_year(['3911'])),
                'montant_net_stock_final' :abs(self.bal_calulator_current_year(['3111','3116']) - self.bal_calulator_current_year(['39111','39116'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39111%'),('code','=like','39116%')]).exists() else abs(self.bal_calulator_current_year(['3111','3116']) - self.bal_calulator_current_year(['3911'])) ,
                'montant_brut_stock_initial' :abs(self.bal_calulator_previous_years(['3111','3116'])),
                'provisions_stock_initial' :abs(self.bal_calulator_previous_years(['39111','39116'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39111%'),('code','=like','39116%')]).exists() else abs(self.bal_calulator_previous_years(['3911'])),
                'montant_net_stock_initial' :abs(self.bal_calulator_previous_years(['3111','3116']) - self.bal_calulator_previous_years(['39111','39116'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39111%'),('code','=like','39116%')]).exists() else abs(self.bal_calulator_previous_years(['3111','3116']) - abs(self.bal_calulator_previous_years(['3911']))),
                'variation_stock' : abs(self.bal_calulator_previous_years(['3111','3116']) - self.bal_calulator_previous_years(['39111','39116']) - (self.bal_calulator_current_year(['3111','3116']) - self.bal_calulator_current_year(['39111','39116']))) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39111%'),('code','=like','39116%')]).exists() else abs(self.bal_calulator_previous_years(['3111','3116']) - self.bal_calulator_previous_years(['3911']) - (self.bal_calulator_current_year(['3111','3116']) - self.bal_calulator_current_year(['3911']))),
            })
            line_2 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Biens Meubles')])
            line_2.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['3112','3118']),
                'provisions_stock_final' :self.bal_calulator_current_year(['39112','39118']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39112%'),('code','=like','39118%')]).exists() else 0,
                'montant_net_stock_final' :self.bal_calulator_current_year(['3112','3118']) - self.bal_calulator_current_year(['39112','39118']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39112%'),('code','=like','39118%')]).exists() else self.bal_calulator_current_year(['3112','3118']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['3112','3118']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['39112','39118']),
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['3112','3118']) - self.bal_calulator_previous_years(['39112','39118'])if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39112%'),('code','=like','39118%')]).exists() else 0,
                'variation_stock' :self.bal_calulator_previous_years(['3112','3118']) - self.bal_calulator_previous_years(['39112','39118']) - (self.bal_calulator_current_year(['3112','3118']) - self.bal_calulator_current_year(['39112','39118'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39112%'),('code','=like','39118%')]).exists() else self.bal_calulator_previous_years(['3112','3118']) - self.bal_calulator_current_year(['3112','3118']),
            })
            line_3 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','- Biens & Produits Destinés à la Revente en l\'état')])
            line_3.write({
                'montant_brut_stock_final':line_1.montant_brut_stock_final + line_2.montant_brut_stock_final,
                'provisions_stock_final' :line_1.provisions_stock_final + line_2.provisions_stock_final,
                'montant_net_stock_final' :line_1.montant_net_stock_final + line_2.montant_net_stock_final,
                'montant_brut_stock_initial' :line_1.montant_brut_stock_initial + line_2.montant_brut_stock_initial,
                'provisions_stock_initial' :line_1.provisions_stock_initial + line_2.provisions_stock_initial,
                'montant_net_stock_initial' :line_1.montant_net_stock_initial + line_2.montant_net_stock_initial,
                'variation_stock' :line_1.variation_stock + line_2.variation_stock,
            })
            line_4 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Matière Premières')])
            line_4.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31212']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391212'])  if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391212%')]).exists() else self.bal_calulator_current_year(['3912']),
                'montant_net_stock_final' :self.bal_calulator_current_year(['31212']) - self.bal_calulator_current_year(['391212']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391212%')]).exists() else self.bal_calulator_current_year(['31212']) - self.bal_calulator_current_year(['3912']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31212']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391212'])  if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391212%')]).exists() else self.bal_calulator_previous_years(['3912']),
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31212']) - self.bal_calulator_previous_years(['391212']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391212%')]).exists() else self.bal_calulator_previous_years(['31212']) - self.bal_calulator_previous_years(['3912']) ,
                'variation_stock' :self.bal_calulator_previous_years(['31212']) - self.bal_calulator_previous_years(['391212']) - (self.bal_calulator_current_year(['31212']) - self.bal_calulator_current_year(['391212']))  if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391212%')]).exists() else self.bal_calulator_previous_years(['31212']) - self.bal_calulator_previous_years(['3912']) - (self.bal_calulator_current_year(['31212']) - self.bal_calulator_current_year(['3912'])),
            })
            line_5 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Matières Consommables')])
            line_5.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31222','31221']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391222','391221']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391222%'),('code','=like','391221%')]).exists() else 0 ,
                'montant_net_stock_final' :self.bal_calulator_current_year(['31222','31221']) - self.bal_calulator_current_year(['391222','391221']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391222%'),('code','=like','391221%')]).exists() else  self.bal_calulator_current_year(['31222','31221']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31222','31221']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391222','391221']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391222%'),('code','=like','391221%')]).exists() else 0,
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31222','31221']) - self.bal_calulator_previous_years(['391222','391221'])  if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391222%'),('code','=like','391221%')]).exists() else self.bal_calulator_previous_years(['31222','31221']),
                'variation_stock' :self.bal_calulator_previous_years(['31222','31221']) - self.bal_calulator_previous_years(['391222','391221']) - (self.bal_calulator_current_year(['31222','31221']) - self.bal_calulator_current_year(['391222','391221'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391222%'),('code','=like','391221%')]).exists() else self.bal_calulator_previous_years(['31222','31221']) - self.bal_calulator_current_year(['31222','31221']),
            })
            line_6 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Pièces Détachées')])
            line_6.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31226','31227']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391226','391227']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391226%'),('code','=like','391227%')]).exists() else 0,
                'montant_net_stock_final' :self.bal_calulator_current_year(['31226','31227']) - self.bal_calulator_current_year(['391226','391227']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391226%'),('code','=like','391227%')]).exists() else self.bal_calulator_current_year(['31226','31227']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31226','31227']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391226','391227']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391226%'),('code','=like','391227%')]).exists() else 0,
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31226','31227']) - self.bal_calulator_previous_years(['391226','391227']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391226%'),('code','=like','391227%')]).exists() else self.bal_calulator_previous_years(['31226','31227']),
                'variation_stock' :self.bal_calulator_previous_years(['31226','31227']) - self.bal_calulator_previous_years(['391226','391227']) - (self.bal_calulator_current_year(['31226','31227']) - self.bal_calulator_current_year(['391226','391227'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391226%'),('code','=like','391227%')]).exists() else self.bal_calulator_previous_years(['31226','31227']) - self.bal_calulator_current_year(['31226','31227']),
            })
            line_7 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Carburants, Lubrifiants Pour Véhicules de transport')])
            line_7.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31223','31224']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391223','391224']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391223%'),('code','=like','391224%')]).exists() else 0,
                'montant_net_stock_final' :self.bal_calulator_current_year(['31223','31224']) - self.bal_calulator_current_year(['391223','391224']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391223%'),('code','=like','391224%')]).exists() else self.bal_calulator_current_year(['31223','31224']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31223','31224']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391223','391224']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391223%'),('code','=like','391224%')]).exists() else 0,
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31223','31224']) - self.bal_calulator_previous_years(['391223','391224']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391223%'),('code','=like','391224%')]).exists() else self.bal_calulator_previous_years(['31223','31224']),
                'variation_stock' :self.bal_calulator_previous_years(['31223','31224']) - self.bal_calulator_previous_years(['391223','391224']) - (self.bal_calulator_current_year(['31223','31224']) - self.bal_calulator_current_year(['391223','391224'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','391223%'),('code','=like','391224%')]).exists() else self.bal_calulator_previous_years(['31223','31224']) - self.bal_calulator_current_year(['31223','31224']) ,
            })
            line_8 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','- Biens & Matière Premières Destinés aux activités de Production & de Transformation')])
            line_8.write({
                'montant_brut_stock_final':line_4.montant_brut_stock_final + line_5.montant_brut_stock_final + line_6.montant_brut_stock_final + line_7.montant_brut_stock_final ,
                'provisions_stock_final' :line_4.provisions_stock_final + line_5.provisions_stock_final + line_6.provisions_stock_final + line_7.provisions_stock_final ,
                'montant_net_stock_final' :line_4.montant_net_stock_final + line_5.montant_net_stock_final + line_6.montant_net_stock_final + line_7.montant_net_stock_final ,
                'montant_brut_stock_initial' :line_4.montant_brut_stock_initial + line_5.montant_brut_stock_initial + line_6.montant_brut_stock_initial + line_7.montant_brut_stock_initial ,
                'provisions_stock_initial' :line_4.provisions_stock_initial + line_5.provisions_stock_initial + line_6.provisions_stock_initial + line_7.provisions_stock_initial ,
                'montant_net_stock_initial' :line_4.montant_net_stock_initial + line_5.montant_net_stock_initial + line_6.montant_net_stock_initial + line_7.montant_net_stock_initial ,
                'variation_stock' :line_4.variation_stock + line_5.variation_stock + line_6.variation_stock + line_7.variation_stock ,
            }) 
            line_9 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Récupérables')])
            line_9.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31233']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391233']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391233%')]).exists() else 0,
                'montant_net_stock_final' :self.bal_calulator_current_year(['31233']) - self.bal_calulator_current_year(['391233']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391233%')]).exists() else self.bal_calulator_current_year(['31233']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31233']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391233']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391233%')]).exists() else 0 ,
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31233']) - self.bal_calulator_previous_years(['391233']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391233%')]).exists() else self.bal_calulator_previous_years(['31233']),
                'variation_stock' :self.bal_calulator_previous_years(['31233']) - self.bal_calulator_previous_years(['391233']) - (self.bal_calulator_current_year(['31233']) - self.bal_calulator_current_year(['391233'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391233%')]).exists() else self.bal_calulator_previous_years(['31233']) - self.bal_calulator_current_year(['31233']),
            }) 
            line_10 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Vendus')])
            line_10.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31232']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391232']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391232%')]).exists() else 0,
                'montant_net_stock_final' :self.bal_calulator_current_year(['31232']) - self.bal_calulator_current_year(['391232']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391232%')]).exists() else self.bal_calulator_current_year(['31232']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31232']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391232']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391232%')]).exists() else 0,
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31232']) - self.bal_calulator_previous_years(['391232']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391232%')]).exists() else self.bal_calulator_previous_years(['31232']),
                'variation_stock' :self.bal_calulator_previous_years(['31232']) - self.bal_calulator_previous_years(['391232']) - (self.bal_calulator_current_year(['31232']) - self.bal_calulator_current_year(['391232'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391232%')]).exists() else self.bal_calulator_previous_years(['31232']) - self.bal_calulator_current_year(['31232']),
            })
            line_11 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Perdus')])
            line_11.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31231']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391231']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391231%')]).exists() else 0,
                'montant_net_stock_final' :self.bal_calulator_current_year(['31231']) - self.bal_calulator_current_year(['391231']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391231%')]).exists() else self.bal_calulator_current_year(['31231']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31231']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391231']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391231%')]).exists() else 0,
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31231']) - self.bal_calulator_previous_years(['391231']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391231%')]).exists() else self.bal_calulator_previous_years(['31231']),
                'variation_stock' :self.bal_calulator_previous_years(['31231']) - self.bal_calulator_previous_years(['391231']) - (self.bal_calulator_current_year(['31231']) - self.bal_calulator_current_year(['391231'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391231%')]).exists() else self.bal_calulator_previous_years(['31231']) - self.bal_calulator_current_year(['31231']),
            })
            line_12 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','- Emballage')])
            line_12.write({
                'montant_brut_stock_final':line_9.montant_brut_stock_final+ line_10.montant_brut_stock_final+ line_11.montant_brut_stock_final,
                'provisions_stock_final' :line_9.provisions_stock_final+ line_10.provisions_stock_final+ line_11.provisions_stock_final,
                'montant_net_stock_final' :line_9.montant_net_stock_final+ line_10.montant_net_stock_final+ line_11.montant_net_stock_final,
                'montant_brut_stock_initial' :line_9.montant_brut_stock_initial+ line_10.montant_brut_stock_initial+ line_11.montant_brut_stock_initial,
                'provisions_stock_initial' :line_9.provisions_stock_initial+ line_10.provisions_stock_initial+ line_11.provisions_stock_initial,
                'montant_net_stock_initial' :line_9.montant_net_stock_initial+ line_10.montant_net_stock_initial+ line_11.montant_net_stock_initial,
                'variation_stock' :line_9.variation_stock+ line_10.variation_stock+ line_11.variation_stock,
            })
            line_13 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','I.STOCKS APPROVISIONNEMENT')])
            line_13.write({
                'montant_brut_stock_final':line_3.montant_brut_stock_final +  line_8.montant_brut_stock_final +  line_12.montant_brut_stock_final,
                'provisions_stock_final' :line_3.provisions_stock_final +  line_8.provisions_stock_final +  line_12.provisions_stock_final,
                'montant_net_stock_final' :line_3.montant_net_stock_final +  line_8.montant_net_stock_final +  line_12.montant_net_stock_final,
                'montant_brut_stock_initial' :line_3.montant_brut_stock_initial +  line_8.montant_brut_stock_initial +  line_12.montant_brut_stock_initial,
                'provisions_stock_initial' :line_3.provisions_stock_initial +  line_8.provisions_stock_initial +  line_12.provisions_stock_initial,
                'montant_net_stock_initial' :line_3.montant_net_stock_initial +  line_8.montant_net_stock_initial +  line_12.montant_net_stock_initial,
                'variation_stock' :line_3.variation_stock +  line_8.variation_stock +  line_12.variation_stock,
            })
            line_14 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','TOTAL STOCKS APPROVISIONNEMENT')])
            line_14.write({
                'montant_brut_stock_final':line_13.montant_brut_stock_final,
                'provisions_stock_final' :line_13.provisions_stock_final,
                'montant_net_stock_final' :line_13.montant_net_stock_final,
                'montant_brut_stock_initial' :line_13.montant_brut_stock_initial,
                'provisions_stock_initial' :line_13.provisions_stock_initial,
                'montant_net_stock_initial' :line_13.montant_net_stock_initial,
                'variation_stock' :line_13.variation_stock,
             
            })
            line_15 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Produits En cours')])
            line_15.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['3131','3138','314']),
                'provisions_stock_final' :self.bal_calulator_current_year(['39131','39138','3914']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39131%'),('code','=like','39138%')]).exists() else self.bal_calulator_current_year(['3913','3914']),
                'montant_net_stock_final' :self.bal_calulator_current_year(['3131','3138','314']) - self.bal_calulator_current_year(['39131','39138','3914']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39131%'),('code','=like','39138%')]).exists() else self.bal_calulator_current_year(['3131','3138','314']) - self.bal_calulator_current_year(['3913','3914']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['3131','3138','314']) ,
                'provisions_stock_initial' :self.bal_calulator_previous_years(['39131','39138','3914']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39131%'),('code','=like','39138%')]).exists() else self.bal_calulator_previous_years(['3913','3914']),
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['3131','3138','314']) - self.bal_calulator_previous_years(['39131','39138','3914']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39131%'),('code','=like','39138%')]).exists() else self.bal_calulator_previous_years(['3131','3138','314']) - self.bal_calulator_previous_years(['3913','3914']),
                'variation_stock' :self.bal_calulator_previous_years(['3131','3138','314']) - self.bal_calulator_previous_years(['39131','39138','3914']) - (self.bal_calulator_current_year(['3131','3138','314']) - self.bal_calulator_current_year(['39131','39138','3914'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39131%'),('code','=like','39138%')]).exists() else self.bal_calulator_previous_years(['3131','3138','314']) - self.bal_calulator_previous_years(['3913','3914']) - (self.bal_calulator_current_year(['3131','3138','314']) - self.bal_calulator_current_year(['3913','3914'])),
            })
            line_16 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Etudes En cours')])
            line_16.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31342']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391342']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391342%')]).exists() else self.bal_calulator_current_year(['3913']),
                'montant_net_stock_final' :self.bal_calulator_current_year(['31342']) - self.bal_calulator_current_year(['391342']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391342%')]).exists() else self.bal_calulator_current_year(['31342']) - self.bal_calulator_current_year(['3913']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31342']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391342']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391342%')]).exists() else 0 ,
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31342']) - self.bal_calulator_previous_years(['391342']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391342%')]).exists() else self.bal_calulator_previous_years(['31342']) - self.bal_calulator_previous_years(['3913']),
                'variation_stock' :self.bal_calulator_previous_years(['31342']) - self.bal_calulator_previous_years(['391342']) - (self.bal_calulator_current_year(['31342']) - self.bal_calulator_current_year(['391342'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391342%')]).exists() else self.bal_calulator_previous_years(['31342']) - self.bal_calulator_previous_years(['3913']) - (self.bal_calulator_current_year(['31342']) - self.bal_calulator_current_year(['3913'])),
            })
            line_17 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Travaux En-cours')])
            line_17.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31341']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391341']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391341%')]).exists() else 0,
                'montant_net_stock_final' :self.bal_calulator_current_year(['31341']) - self.bal_calulator_current_year(['391341']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391341%')]).exists() else self.bal_calulator_current_year(['31341']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31341']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391341']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391341%')]).exists() else 0,
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31341']) - self.bal_calulator_previous_years(['391341']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391341%')]).exists() else self.bal_calulator_previous_years(['31341']),
                'variation_stock' :self.bal_calulator_previous_years(['31341']) - self.bal_calulator_previous_years(['391341']) - (self.bal_calulator_current_year(['31341']) - self.bal_calulator_current_year(['391341'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391341%')]).exists() else self.bal_calulator_previous_years(['31341'])  - self.bal_calulator_current_year(['31341']) ,
            })
            line_18 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Services En-cours')])
            line_18.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31343']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391343']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391343%')]).exists() else 0,
                'montant_net_stock_final' :self.bal_calulator_current_year(['31343']) - self.bal_calulator_current_year(['391343']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391343%')]).exists() else self.bal_calulator_current_year(['31343']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31343']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391343'])  if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391343%')]).exists() else 0,
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31343']) - self.bal_calulator_previous_years(['391343'])  if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391343%')]).exists() else self.bal_calulator_previous_years(['31343']),
                'variation_stock' :self.bal_calulator_previous_years(['31343']) - self.bal_calulator_previous_years(['391343']) - (self.bal_calulator_current_year(['31343']) - self.bal_calulator_current_year(['391343']))  if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391343%')]).exists() else self.bal_calulator_previous_years(['31343']) - self.bal_calulator_current_year(['31343']),
            })
            line_19 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','II.STOCK EN-COURS PRODUCTION DE BIENS & SERVICE')])
            line_19.write({
                'montant_brut_stock_final':line_15.montant_brut_stock_final +  line_16.montant_brut_stock_final +  line_17.montant_brut_stock_final +line_18.montant_brut_stock_final,
                'provisions_stock_final' :line_15.provisions_stock_final +  line_16.provisions_stock_final +  line_17.provisions_stock_final +line_18.provisions_stock_final,
                'montant_net_stock_final' :line_15.montant_net_stock_final +  line_16.montant_net_stock_final +  line_17.montant_net_stock_final +line_18.montant_net_stock_final,
                'montant_brut_stock_initial' :line_15.montant_brut_stock_initial +  line_16.montant_brut_stock_initial +  line_17.montant_brut_stock_initial +line_18.montant_brut_stock_initial,
                'provisions_stock_initial' :line_15.provisions_stock_initial +  line_16.provisions_stock_initial +  line_17.provisions_stock_initial +line_18.provisions_stock_initial,
                'montant_net_stock_initial' :line_15.montant_net_stock_initial +  line_16.montant_net_stock_initial +  line_17.montant_net_stock_initial +line_18.montant_net_stock_initial,
                'variation_stock' :line_15.variation_stock +  line_16.variation_stock +  line_17.variation_stock +line_18.variation_stock,
            })
            line_20 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','TOTAL STOCKS DES EN-COURS')])
            line_20.write({
                'montant_brut_stock_final':line_19.montant_brut_stock_final,
                'provisions_stock_final' :line_19.provisions_stock_final,
                'montant_net_stock_final' :line_19.montant_net_stock_final,
                'montant_brut_stock_initial' :line_19.montant_brut_stock_initial,
                'provisions_stock_initial' :line_19.provisions_stock_initial,
                'montant_net_stock_initial' :line_19.montant_net_stock_initial,
                'variation_stock' :line_19.variation_stock,
            })
            line_21 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Produits Finis')])
            line_21.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['3151','3152']),
                'provisions_stock_final' :self.bal_calulator_current_year(['39151','39152']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39151%'),('code','=like','39152%')]).exists() else self.bal_calulator_current_year(['3915']),
                'montant_net_stock_final' :self.bal_calulator_current_year(['3151','3152']) - self.bal_calulator_current_year(['39151','39152']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39151%'),('code','=like','39152%')]).exists() else self.bal_calulator_current_year(['3151','3152']) - self.bal_calulator_current_year(['3915']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['3151','3152']) ,
                'provisions_stock_initial' :self.bal_calulator_previous_years(['39151','39152']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39151%'),('code','=like','39152%')]).exists() else self.bal_calulator_previous_years(['3915']),
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['3151','3152']) - self.bal_calulator_previous_years(['39151','39152']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39151%'),('code','=like','39152%')]).exists() else self.bal_calulator_previous_years(['3151','3152'])  - self.bal_calulator_previous_years(['3915']),
                'variation_stock' :self.bal_calulator_previous_years(['3151','3152']) - self.bal_calulator_previous_years(['39151','39152']) - (self.bal_calulator_current_year(['3151','3152']) - self.bal_calulator_current_year(['39151','39152'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39151%'),('code','=like','39152%')]).exists() else  self.bal_calulator_previous_years(['3151','3152']) - self.bal_calulator_previous_years(['3915']) - (self.bal_calulator_current_year(['3151','3152']) - self.bal_calulator_current_year(['3915'])),
            
            })
            line_22 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Biens Finis')])
            line_22.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['3156','3158']),
                'provisions_stock_final' :self.bal_calulator_current_year(['39156','39158']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39156%'),('code','=like','39158%')]).exists() else 0,
                'montant_net_stock_final' :self.bal_calulator_current_year(['3156','3158']) - self.bal_calulator_current_year(['39156','39158']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39156%'),('code','=like','39158%')]).exists() else self.bal_calulator_current_year(['3156','3158']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['3156','3158']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['39156','39158']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39156%'),('code','=like','39158%')]).exists() else 0,
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['3156','3158']) - self.bal_calulator_previous_years(['39156','39158']) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39156%'),('code','=like','39158%')]).exists() else self.bal_calulator_previous_years(['3156','3158']),
                'variation_stock' :self.bal_calulator_previous_years(['3156','3158']) - self.bal_calulator_previous_years(['39156','39158']) - (self.bal_calulator_current_year(['3156','3158']) - self.bal_calulator_current_year(['39156','39158'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),'|',('code','=like','39156%'),('code','=like','39158%')]).exists() else self.bal_calulator_previous_years(['3156','3158']) - self.bal_calulator_current_year(['3156','3158']),
            
            })
            line_23 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','III.STOCK PRODUITS FINIS')])
            line_23.write({
                'montant_brut_stock_final':line_21.montant_brut_stock_final  + line_22.montant_brut_stock_final,
                'provisions_stock_final' :line_21.provisions_stock_final  + line_22.provisions_stock_final,
                'montant_net_stock_final' :line_21.montant_net_stock_final  + line_22.montant_net_stock_final,
                'montant_brut_stock_initial' :line_21.montant_brut_stock_initial  + line_22.montant_brut_stock_initial,
                'provisions_stock_initial' :line_21.provisions_stock_initial  + line_22.provisions_stock_initial,
                'montant_net_stock_initial' :line_21.montant_net_stock_initial  + line_22.montant_net_stock_initial,
                'variation_stock' :line_21.variation_stock  + line_22.variation_stock,
            })
            line_24 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','TOTAL STOCKS PRODUITS & BIENS FINIS')])
            line_24.write({
                'montant_brut_stock_final':line_23.montant_brut_stock_final,
                'provisions_stock_final' :line_23.provisions_stock_final,
                'montant_net_stock_final' :line_23.montant_net_stock_final,
                'montant_brut_stock_initial' :line_23.montant_brut_stock_initial,
                'provisions_stock_initial' :line_23.provisions_stock_initial,
                'montant_net_stock_initial' :line_23.montant_net_stock_initial,
                'variation_stock' :line_23.variation_stock,
            })
            line_25 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Déchets')])
            line_25.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31451']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391451']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391451%')]).exists() else self.bal_calulator_current_year(['3914']),
                'montant_net_stock_final' :self.bal_calulator_current_year(['31451']) - self.bal_calulator_current_year(['391451']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391451%')]).exists() else self.bal_calulator_current_year(['31451']) -  self.bal_calulator_current_year(['3914']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31451']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391451']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391451%')]).exists() else self.bal_calulator_previous_years(['3914']),
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31451']) - self.bal_calulator_previous_years(['391451']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391451%')]).exists() else self.bal_calulator_previous_years(['31451']) - self.bal_calulator_previous_years(['3914']),
                'variation_stock' :self.bal_calulator_previous_years(['31451']) - self.bal_calulator_previous_years(['391451']) - (self.bal_calulator_current_year(['31451']) - self.bal_calulator_current_year(['391451'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391451%')]).exists() else self.bal_calulator_previous_years(['31451']) - self.bal_calulator_previous_years(['3914']) - (self.bal_calulator_current_year(['31451']) - self.bal_calulator_current_year(['3914'])),
            })
            line_26 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Rebuts')])
            line_26.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31452']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391452']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391452%')]).exists() else 0,
                'montant_net_stock_final' :self.bal_calulator_current_year(['31452']) - self.bal_calulator_current_year(['391452']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391452%')]).exists() else self.bal_calulator_current_year(['31452']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31452']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391452']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391452%')]).exists() else 0,
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31452']) - self.bal_calulator_previous_years(['391452']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391452%')]).exists() else self.bal_calulator_previous_years(['31452']),
                'variation_stock' :self.bal_calulator_previous_years(['31452']) - self.bal_calulator_previous_years(['391452']) - (self.bal_calulator_current_year(['31452']) - self.bal_calulator_current_year(['391452'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391452%')]).exists() else self.bal_calulator_previous_years(['31452'])  - self.bal_calulator_current_year(['31452']),
            
            })
            # --------------------------------------------------
            line_27 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','* Matières de Récupération')])
            line_27.write({
                'montant_brut_stock_final':self.bal_calulator_current_year(['31453']),
                'provisions_stock_final' :self.bal_calulator_current_year(['391453']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391453%')]).exists() else 0,
                'montant_net_stock_final' :self.bal_calulator_current_year(['31453']) - self.bal_calulator_current_year(['391453'])if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391453%')]).exists() else self.bal_calulator_current_year(['31453']),
                'montant_brut_stock_initial' :self.bal_calulator_previous_years(['31453']),
                'provisions_stock_initial' :self.bal_calulator_previous_years(['391453']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391453%')]).exists() else 0 ,
                'montant_net_stock_initial' :self.bal_calulator_previous_years(['31453']) - self.bal_calulator_previous_years(['391453']) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391453%')]).exists() else self.bal_calulator_previous_years(['31453']),
                'variation_stock' :self.bal_calulator_previous_years(['31453']) - self.bal_calulator_previous_years(['391453']) - (self.bal_calulator_current_year(['31453']) - self.bal_calulator_current_year(['391453'])) if self.env['account.account'].search([('company_id','=',self.env.company.id),('code','=like','391453%')]).exists() else self.bal_calulator_previous_years(['31453']) - self.bal_calulator_current_year(['31453']),
            
            })
            line_28 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','IV.STOCK PRODUITS RESIDUELS')])
            line_28.write({
                'montant_brut_stock_final':line_25.montant_brut_stock_final +  line_26.montant_brut_stock_final +  line_27.montant_brut_stock_final,
                'provisions_stock_final' :line_25.provisions_stock_final +  line_26.provisions_stock_final +  line_27.provisions_stock_final,
                'montant_net_stock_final' :line_25.montant_net_stock_final +  line_26.montant_net_stock_final +  line_27.montant_net_stock_final,
                'montant_brut_stock_initial' :line_25.montant_brut_stock_initial +  line_26.montant_brut_stock_initial +  line_27.montant_brut_stock_initial,
                'provisions_stock_initial' :line_25.provisions_stock_initial +  line_26.provisions_stock_initial +  line_27.provisions_stock_initial,
                'montant_net_stock_initial' :line_25.montant_net_stock_initial +  line_26.montant_net_stock_initial +  line_27.montant_net_stock_initial,
                'variation_stock' :line_25.variation_stock +  line_26.variation_stock +  line_27.variation_stock,
            })
            line_29 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','TOTAL STOCKS PRODUITS RESIDUELS')])
            line_29.write({
                'montant_brut_stock_final':line_28.montant_brut_stock_final,
                'provisions_stock_final' :line_28.provisions_stock_final,
                'montant_net_stock_final' :line_28.montant_net_stock_final,
                'montant_brut_stock_initial' :line_28.montant_brut_stock_initial,
                'provisions_stock_initial' :line_28.provisions_stock_initial,
                'montant_net_stock_initial' :line_28.montant_net_stock_initial,
                'variation_stock' :line_28.variation_stock,
            })
            line_30 = self.env['detail.stock.line'].search([('detail_stock_id','=',rec.id),('name','=','TOTAL  GENERAL')])
            line_30.write({
                'montant_brut_stock_final':line_29.montant_brut_stock_final + line_24.montant_brut_stock_final + line_20.montant_brut_stock_final + line_14.montant_brut_stock_final,
                'provisions_stock_final' :line_29.provisions_stock_final + line_24.provisions_stock_final + line_20.provisions_stock_final + line_14.provisions_stock_final,
                'montant_net_stock_final' :line_29.montant_net_stock_final + line_24.montant_net_stock_final + line_20.montant_net_stock_final + line_14.montant_net_stock_final,
                'montant_brut_stock_initial' :line_29.montant_brut_stock_initial + line_24.montant_brut_stock_initial + line_20.montant_brut_stock_initial + line_14.montant_brut_stock_initial,
                'provisions_stock_initial' :line_29.provisions_stock_initial + line_24.provisions_stock_initial + line_20.provisions_stock_initial + line_14.provisions_stock_initial,
                'montant_net_stock_initial' :line_29.montant_net_stock_initial + line_24.montant_net_stock_initial + line_20.montant_net_stock_initial + line_14.montant_net_stock_initial,
                'variation_stock' :line_29.variation_stock + line_24.variation_stock + line_20.variation_stock + line_14.variation_stock,
            })
            
     
    def get_xml(self,parent):
        for rec in self:
            if rec.detail_stock_line_ids:
                tableau = etree.SubElement(parent, "tableau")
                etree.SubElement(tableau,"id").text = str(36) # read documentation XML
                group_valeurs = etree.SubElement(parent, "groupeValeurs")
                for line in rec.detail_stock_line_ids:
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_montant_brut_stock_final)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_brut_stock_final)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_provisions_stock_final)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.provisions_stock_final)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_montant_net_stock_final)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_net_stock_final)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_montant_brut_stock_initial)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_brut_stock_initial)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_provisions_stock_initial)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.provisions_stock_initial)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_montant_net_stock_initial)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.montant_net_stock_initial)
                    
                    valeur_cellule = etree.SubElement(group_valeurs, "ValeurCellule")
                    cellule = etree.SubElement(valeur_cellule, "cellule")
                    etree.SubElement(cellule, "codeEdi").text = str(line.edi_variation_stock)
                    etree.SubElement(valeur_cellule, "valeur").text = str(line.variation_stock)

                extra_field_valeurs = etree.SubElement(parent, "extraFieldvaleurs")

            else:
                pass
        
class DetailStockLine(models.Model):
    _name = 'detail.stock.line'
    _description = 'LIGNES Detail Stock'

    name = fields.Char(string=u"Stock",required=True,readonly=True)
    # fy_n_id = fields.Many2one('date.range', 'Exercice fiscal')
    code_1 = fields.Char(string=u"Code 1",  )
    code_2 = fields.Char(string=u"Code 2",  )
    montant_brut_stock_final = fields.Float(string=u"Montant brut Final",  required=False, )
    provisions_stock_final = fields.Float(string=u"Provision pour dépréciation Final",  required=False, )
    montant_net_stock_final = fields.Float(string=u"Montant net Final",  required=False, )
    montant_brut_stock_initial = fields.Float(string=u"Montant brut Initial",  required=False, )
    provisions_stock_initial = fields.Float(string=u"Provision pour dépréciation Initial",  required=False, )
    montant_net_stock_initial = fields.Float(string=u"Montant net Initial",  required=False, )
    variation_stock = fields.Float(string=u"Variation de stock",  required=False, store=True,)
    
    # Code Edi 
    edi_montant_brut_stock_final = fields.Integer(string=u"Montant brut Final",  required=False, readonly=True)
    edi_provisions_stock_final = fields.Integer(string=u"Provision pour dépréciation Final",  required=False, readonly=True )
    edi_montant_net_stock_final = fields.Integer(string=u"Montant net Final",  required=False,  readonly=True)
    edi_montant_brut_stock_initial = fields.Integer(string=u"Montant brut Initial",  required=False,  readonly=True)
    edi_provisions_stock_initial = fields.Integer(string=u"Provision pour dépréciation Initial",  required=False,  readonly=True)
    edi_montant_net_stock_initial = fields.Integer(string=u"Montant net Initial",  required=False, readonly=True )
    edi_variation_stock = fields.Integer(string=u"Variation de stock",  required=False, store=True, readonly=True)
    
    # Relational Fields
    detail_stock_id = fields.Many2one(comodel_name="detail.stock", string=u"Detail Stock", required=False, )
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('detail.stock.line'))
        