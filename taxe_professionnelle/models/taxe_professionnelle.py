# -*- coding: utf-8 -*-

from odoo import models, fields, api
import os
directory = os.path.dirname(__file__)

import base64
try:
    from openpyxl import load_workbook
except ImportError:
    pass
from openpyxl.styles import Border, Side, Font
import io
from string import ascii_lowercase
import itertools


def iter_all_strings():
    size = 1
    while True:
        for s in itertools.product(ascii_lowercase, repeat=size):
            yield "".join(s)
        size += 1

class TaxeProfessionnelle(models.Model):
    _name = "taxe.professionnelle"
    _description = "Taxe Professionnelle"
    _inherit = ['mail.thread']


    name = fields.Char(string=u'Description', required=True)
    date = fields.Date(string=u'Date', required=True)
    fiscal_year_id = fields.Many2one('date.range',string=u'Exercice fiscal',domain=[('type_id.fiscal_year','=',True)], required=True)
    company_id = fields.Many2one('res.company',string=u'Société',default=lambda self: self.env.user.company_id,
                                 required=False)
    type_declaration = fields.Selection(string=u"Type Déclaration", selection=[('initiale', u'Déclaration initiale'),
                                                                               ('modificative', u'Déclaration modificative'), ], required=True, )
    asset_succursale_id = fields.Many2one(comodel_name="asset.succursale", string=u"Succursale", required=True, )
    line_terrains_ids = fields.One2many(comodel_name='taxe.professionnelle.terrains', inverse_name='taxe_professionnelle_id',string=u'Terrains')
    line_materiel_ids = fields.One2many(comodel_name='taxe.professionnelle.materiel', inverse_name='taxe_professionnelle_id',string=u'Matériels et outillages')
    line_cession_ids = fields.One2many(comodel_name='taxe.professionnelle.cession', inverse_name='taxe_professionnelle_id',string=u'Cessions')

    tp_rapport_excel = fields.Binary(string="Fichier Excel")

    state = fields.Selection([
        ('draft', u'Brouillon'),
        ('done', u'Valide')], default='draft', string='Etat', readonly=True, track_visibility='onchange')

    # @api.multi
    def generate_data(self):
        account_asset_obj = self.env['account.asset.asset']
        taxe_professionnelle_terrains_obj = self.env['taxe.professionnelle.terrains']
        taxe_professionnelle_materiel_obj = self.env['taxe.professionnelle.materiel']
        taxe_professionnelle_cession_obj = self.env['taxe.professionnelle.cession']
        for record in self:
            record.line_terrains_ids.unlink()
            record.line_materiel_ids.unlink()
            record.line_cession_ids.unlink()
            #Terrains
            domain_terrains = [('date', '>=', self.fiscal_year_id.date_start),
                                ('date', '<=', self.fiscal_year_id.date_end),
                                ('asset_succursale_id', '<=', self.asset_succursale_id.id),
                                '|',('category_id.account_immo_id.code', '=like', '231%'),('category_id.account_immo_id.code', '=like', '232%'),
                                ('state', '=', 'open')]
            asset_terrains_ids = account_asset_obj.search(domain_terrains)
            for terrain in asset_terrains_ids:
                if terrain.category_id.account_immo_id.code.startswith('231') and not terrain.category_id.account_immo_id.code.startswith('2316'):
                    nature = 'terrains'
                elif terrain.category_id.account_immo_id.code.startswith('232') and not terrain.category_id.account_immo_id.code.startswith('2327'):
                    nature = 'constructions'
                else:
                    nature = 'agencements'
                terrain_vals = {
                        'nature':nature,
                        'n_titre_foncier':terrain.n_titre_foncier,
                        'name':terrain.name,
                        'superficie':terrain.superficie,
                        'statut':terrain.statut,
                        'price':terrain.value,
                        'date_acquisition':terrain.invoice_date,
                        'taxe_professionnelle_id':record.id,
                        }
                taxe_professionnelle_terrains_obj.create(terrain_vals)
            #Materiels
            domain_materiel = [('date', '>=', self.fiscal_year_id.date_start),
                                ('date', '<=', self.fiscal_year_id.date_end),
                                ('asset_succursale_id', '<=', self.asset_succursale_id.id),
                                '|',('category_id.account_immo_id.code', '=like', '233%'),
                                ('category_id.account_immo_id.code', '=like', '235%'),
                                ('state', '=', 'open')]
            asset_materiel_ids = account_asset_obj.search(domain_materiel)
            for materiel in asset_materiel_ids:
                if not materiel.category_id.account_immo_id.code.startswith('2351'):
                    materiel_vals = {
                            'name':materiel.name,
                            'state':materiel.type_acquisition,
                            'date_acquisition':materiel.invoice_date,
                            'date_service':materiel.date,
                            'price':materiel.value,
                            'taxe_professionnelle_id':record.id,
                            }
                    taxe_professionnelle_materiel_obj.create(materiel_vals)
            #Cessions
            domain_cessions = [('date', '>=', self.fiscal_year_id.date_start),
                                ('date', '<=', self.fiscal_year_id.date_end),
                                ('asset_succursale_id', '<=', self.asset_succursale_id.id),
                                ('state', '=', 'close')]
            asset_cessions_ids = account_asset_obj.search(domain_cessions)
            for cession in asset_cessions_ids:
                if not cession.category_id.account_immo_id.code.startswith('234') and not cession.category_id.account_immo_id.code.startswith('2351'):
                    cession_vals = {
                            'name':cession.name,
                            'titre':cession.n_titre_foncier,
                            'date_acquisition':cession.invoice_date,
                            'date_cession':cession.date_cession,
                            'price_acquision':cession.value,
                            'price_cession':cession.sold_amount,
                            'taxe_professionnelle_id':record.id,
                            }
                    taxe_professionnelle_cession_obj.create(cession_vals)

    # @api.multi
    def genetare_tp_file(self):
        report_template = self.env['ir.config_parameter'].sudo().get_param('taxe_professionnelle.tp_rapport_excel')
        for record in self:
            file = base64.b64decode(report_template)
            xls_filelike = io.BytesIO(file)
            wb = load_workbook(xls_filelike)
            sheet1 = wb.worksheets[0]
            sheet2 = wb.worksheets[1]
            sheet3 = wb.worksheets[2]
            sheet4 = wb.worksheets[3]
            sheet5 = wb.worksheets[4]

            border_top = Border(
                            top=Side(border_style='thin',),
                            )
            border_bottom = Border(
                            bottom=Side(border_style='thin',),
                            )
            border_right = Border(
                            right=Side(border_style='thin',),
                            )
            border_top_bottom_right = Border(
                            right=Side(border_style='thin',),
                            bottom=Side(border_style='thin',),
                            top=Side(border_style='thin',),
                            )
            border_bottom_right = Border(
                            right=Side(border_style='thin',),
                            bottom=Side(border_style='thin',),
                            )
            #TABLE 0 INFOS
            if record.type_declaration == 'initiale':
                sheet1['I13'] = u"Déclaration initiale"
            else:
                sheet1['I13'] = u"Déclaration modificative"

            sheet1['F17'] = record.company_id.partner_id.id_fisc
            sheet1['N20'] = record.company_id.partner_id.itp
            sheet1['N22'] = record.asset_succursale_id.itp
            sheet1['I24'] = record.company_id.partner_id.name
            sheet1['H28'] = record.company_id.partner_id.rc
            sheet1['B31'] = record.company_id.partner_id.street
            sheet1['E35'] = record.company_id.partner_id.phone
            sheet1['O35'] = record.company_id.partner_id.fax
            sheet1['D37'] = record.company_id.partner_id.email
            sheet1['I38'] = record.company_id.partner_id.activites
            sheet1['K49'] = record.company_id.partner_id.city
            sheet1['P49'] = record.date
            #TABLE 1
            for s in iter_all_strings():
                sheet2[s+'8'].border = border_top
                if s == 'ap':
                    break
            for s in iter_all_strings():
                sheet2[s+'10'].border = border_bottom
                if s == 'ap':
                    break
            sheet2['AQ8'].border = border_top_bottom_right
            sheet2['AQ9'].border = border_top_bottom_right
            sheet2['AQ10'].border = border_top_bottom_right
            j = 11
            total = 0.0
            for terrain in record.line_terrains_ids:
                sheet2['B' + str(j)] = terrain.nature
                sheet2['H' + str(j)] = terrain.n_titre_foncier
                sheet2['N' + str(j)] = terrain.name
                sheet2['T' + str(j)] = terrain.superficie
                sheet2['Z' + str(j)] = terrain.statut
                sheet2['AF' + str(j)] = terrain.price
                sheet2['AL' + str(j)] = terrain.date_acquisition

                sheet2['AQ' + str(j)].border = border_right
                j+=1
                total += terrain.price
            sheet2['AQ' + str(j)].border = border_bottom_right
            for s in iter_all_strings():
                sheet2[s+str(j)].border = border_bottom
                if s == 'ap':
                    break

            sheet2['Z' + str(j+1)] = "TOTAL"
            sheet2['AF' + str(j+1)] = total

            sheet2['AH' + str(j+2)] = "Cachet et signature :"

            #TABLE 2
            for s in iter_all_strings():
                sheet3[s+'8'].border = border_top
                if s == 'ap':
                    break
            for s in iter_all_strings():
                sheet3[s+'10'].border = border_bottom
                if s == 'ap':
                    break
            sheet3['AQ8'].border = border_top_bottom_right
            sheet3['AQ9'].border = border_top_bottom_right
            sheet3['AQ10'].border = border_top_bottom_right
            j = 11
            total_materiel = 0.0
            for materiel in record.line_materiel_ids:
                sheet3['B' + str(j)] = materiel.name
                sheet3['P' + str(j)] = materiel.state
                sheet3['V' + str(j)] = materiel.date_acquisition
                sheet3['AD' + str(j)] = materiel.date_service
                sheet3['AJ' + str(j)] = materiel.price

                sheet3['AQ' + str(j)].border = border_right
                j+=1
                total_materiel += materiel.price
            sheet3['AQ' + str(j)].border = border_bottom_right
            for s in iter_all_strings():
                sheet3[s+str(j)].border = border_bottom
                if s == 'ap':
                    break

            sheet3['AD' + str(j+1)] = "TOTAL"
            sheet3['AJ' + str(j+1)] = total_materiel

            sheet3['AJ' + str(j+2)] = "Cachet et signature :"
            #TABLE 3
            for s in iter_all_strings():
                sheet4[s+'8'].border = border_top
                if s == 'ap':
                    break
            for s in iter_all_strings():
                sheet4[s+'10'].border = border_bottom
                if s == 'ap':
                    break
            sheet4['AQ8'].border = border_top_bottom_right
            sheet4['AQ9'].border = border_top_bottom_right
            sheet4['AQ10'].border = border_top_bottom_right
            j = 11
            total_cession = 0.0
            for cession in record.line_cession_ids:
                sheet4['B' + str(j)] = cession.name
                sheet4['N' + str(j)] = cession.titre
                sheet4['T' + str(j)] = cession.date_acquisition
                sheet4['Z' + str(j)] = cession.date_cession
                sheet4['AF' + str(j)] = cession.price_acquision
                sheet4['AL' + str(j)] = cession.price_cession

                sheet4['AQ' + str(j)].border = border_right
                j += 1
                total_cession += cession.price_cession
            sheet4['AQ' + str(j)].border = border_bottom_right
            for s in iter_all_strings():
                sheet4[s+str(j)].border = border_bottom
                if s == 'ap':
                    break

            sheet4['AL' + str(j+2)] = "Cachet et signature :"
            #TABLE 4
            sheet5['Q25'] = record.fiscal_year_id.name
            sheet5['E28'] = record.company_id.partner_id.name
            sheet5['K31'] = record.company_id.partner_id.id_fisc

            wb.save(os.path.join(directory,"tp.xlsx"))
            tp_report_file = base64.encodestring(open(os.path.join(directory,'tp.xlsx'), 'rb').read())
            record.write({'tp_rapport_excel': tp_report_file})
        return True

class TaxeProfessionnelleTerrains(models.Model):
    _name = "taxe.professionnelle.terrains"
    _description = "Taxe Professionnelle Terrains"

    nature = fields.Selection(string="Nature", selection=[('terrains', u'Terrains'),
                                                          ('constructions', u'Constructions'),
                                                          ('agencements', u'Agencements et Aménagements'),
                                                          ], required=False, )
    n_titre_foncier = fields.Char(string=u"N° du titre foncier ou de la réquisition", required=False)
    name = fields.Char(string=u"Consistance/Description", required=False, )
    superficie = fields.Float(string=u"Superficie en m²",  required=False, )
    statut = fields.Char(string=u"Statut patrimonial du bien (propriété,location ou autre…)", required=False, )
    price = fields.Float(string=u"Prix d’acquisition ou coût de revient ou montant annuel du bail (en dirhams et hors Taxe)",  required=False, )
    date_acquisition = fields.Date(string=u"Date d’acquisition, d’achèvement ou de location", required=False,)
    taxe_professionnelle_id = fields.Many2one(comodel_name="taxe.professionnelle", string="TP", required=False, )

class TaxeProfessionnelleMateriel(models.Model):
    _name = "taxe.professionnelle.materiel"
    _description = "Taxe Professionnelle Materiel"

    name = fields.Char(string=u"Désignation et référence", required=False, )
    state = fields.Selection(string="Etat", selection=[('n', 'Neuf(N)'), ('o', 'Occasion(O)')], required=False, )
    date_acquisition = fields.Date(string=u"Date d’acquisition", required=False,)
    date_service = fields.Date(string=u"Date de mise en service ou d’installation", required=False,)
    price = fields.Float(
        string=u"Prix d’acquisition ou coût de revient ou montant annuel du bail (en dirhams et hors Taxe )",
        required=False, )
    taxe_professionnelle_id = fields.Many2one(comodel_name="taxe.professionnelle", string="TP", required=False, )

class TaxeProfessionnelleCession(models.Model):
    _name = "taxe.professionnelle.cession"
    _description = "Taxe Professionnelle Cession"

    name = fields.Char(string=u"Nature et/ou désignation et référence", required=False, )
    titre = fields.Char(string=u"N° du titre foncier", required=False, )
    date_acquisition = fields.Date(string=u"Date d’acquisition", required=False,)
    date_cession = fields.Date(string=u"Date de retrait ou de cession", required=False,)
    price_acquision = fields.Float(
        string=u"Prix d’acquisition ou coût de revient ou  montant annuel du  bail)",
        required=False, )
    price_cession = fields.Float(
        string=u"Prix de cession ou valeur au moment du retrait)",
        required=False, )
    taxe_professionnelle_id = fields.Many2one(comodel_name="taxe.professionnelle", string="TP", required=False, )