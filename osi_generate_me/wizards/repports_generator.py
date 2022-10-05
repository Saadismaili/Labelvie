import datetime
import base64
import zipfile
import lxml
import xlwt
import io
from datetime import datetime, timedelta
import base64
from lxml import etree
from openerp import models, api, fields , _
from openerp.exceptions import UserError
from openerp.tools.safe_eval import safe_eval

import os
directory = os.path.dirname(__file__)

class RepportGenerator(models.TransientModel):
    _name = 'report.generator'

    xml_file = fields.Binary(u'Fichier XML')
    name = fields.Char('Nom du fichier', readonly=True)
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal',copy=False)
    boolean = fields.Boolean(string='Voulez-vous générer tout la liasse fiscal ?', default=True)
    # XML PART
    fiscal_model = fields.Char(string='Model fiscal')
    xml_bool  = fields.Boolean(string='Voulez-vous générer xml ?')
    model_id = fields.Many2one(string='Liasse fiscal', comodel_name='liass.fiscal')
    models_ids = fields.Many2many('liass.fiscal.line')
    company_id = fields.Many2one('res.company', readonly=True, string=u'Societé',
                                default=lambda self: self.env['res.company']._company_default_get('report.generator'))
    
    
    def confirm_models_calculations(self):
        if self.boolean:
            for model in self.model_id.line_ids:
                    object_ = self.env[model.model].search([('fy_n_id','=',self.fy_n_id.id)])
                    if object_.exists():
                        object_.get_lines()
                        object_.get_lines()
                    else:
                        self.env[model.model].create({
                            'fy_n_id': self.fy_n_id.id,
                        })
                        object_ = self.env[model.model].search([('id','!=',False)],order = 'id desc',limit=1)
                        object_.write({
                        'fy_n_id': self.fy_n_id.id, 
                        }) 
                        object_.get_lines() 
                        object_.get_lines() 
        else:
            for model in self.models_ids:
                    object_ = self.env[model.model].search([('fy_n_id','=',self.fy_n_id.id)])
                    if object_.exists():
                        object_.get_lines()
                        object_.get_lines()
                    else:
                        self.env[model.model].create({
                            'fy_n_id': self.fy_n_id.id,
                        })
                        object_ = self.env[model.model].search([('id','!=',False)],order = 'id desc',limit=1)
                        object_.write({
                        'fy_n_id': self.fy_n_id.id, 
                        }) 
                        object_.get_lines() 
                        object_.get_lines() 
    
    def print_pdf(self):
        if self.boolean:
            self.confirm_models_calculations()     
            return self.env.ref('osi_generate_me.action_report_generator').report_action(self, config=False)
        else:
            self.confirm_models_calculations()
            return self.env.ref('osi_generate_me.action_report_generator_specific_models').report_action(self, config=False) 
    
    def print_xlrd(self):
        self.confirm_models_calculations() 
        data = {
         'fy_n_id': self.fy_n_id.id, 
         'company_id': self.company_id.id,
         'boolean': self.boolean,    
         'model_id': self.model_id.id,    
        }
        return self.env.ref('osi_generate_me.action_osi_generate_me_xlsx_report').report_action(self, data=data) 
        
    def print_xml(self):
        self.confirm_models_calculations()
        root = etree.Element("Liasse")
        model = etree.SubElement(root, "modele")
        etree.SubElement(model, "id").text = str(self.fiscal_model)
        resultat_fiscal = etree.SubElement(root, "resultatFiscal")
        etree.SubElement(resultat_fiscal,"identifiantFiscal").text = str(self.company_id.partner_id.id_fisc)
        etree.SubElement(resultat_fiscal,"exerciceFiscalDu").text = str(self.fy_n_id.date_start)
        etree.SubElement(resultat_fiscal,"exerciceFiscalAu").text = str(self.fy_n_id.date_end)
        group_valeurs_tableau = etree.SubElement(root, "groupeValeursTableau")
        valeurs_tableau = etree.SubElement(group_valeurs_tableau, "ValeursTableau")
        if self.boolean:
            for model in self.model_id.line_ids: 
                self.env[model.model].search([('fy_n_id','=',self.fy_n_id.id)]).get_xml(valeurs_tableau)
        else:
            for model in self.models_ids: 
                self.env[model.model].search([('fy_n_id','=',self.fy_n_id.id)]).get_xml(valeurs_tableau)
        file=base64.encodestring(etree.tostring(root, pretty_print=True))
        # get base url
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        # create attachment
        attachment_id = attachment_obj.create(
            {'name': "simple_is",'store_fname':"simple_is.xml","mimetype":"text/xml", 'datas': file})
        # prepare download url
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        # download
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new"}
    
class OsiGenerateMeXlsxReport(models.AbstractModel):
    _name = 'report.osi_generate_me.report_generator'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners=None):
        domain = []
        if data.get('fy_n_id'):
            domain.append(('fy_n_id', '=', data.get('fy_n_id')))
        if data.get('company_id'):
            domain.append(('company_id', '=', data.get('company_id')))
        
        sheet = workbook.add_worksheet('Garde')
        bold = workbook.add_format({'bold': True, 'align': 'left',})
        border_top_header = workbook.add_format({ 'align': 'center',})
        border_top_header_2 = workbook.add_format({ 'align': 'left',})
        top_top = workbook.add_format({ 'align': 'center',})
        top_left = workbook.add_format({ 'align': 'center',})
        top_right = workbook.add_format({ 'align': 'center',})
        bottom = workbook.add_format({ 'align': 'center',})
        top_top.set_top(1)
        top_left.set_left(1)
        top_left.set_top(1)
        top_right.set_right(1)
        top_right.set_top(1)
        bottom.set_left(1)
        bottom.set_right(1)
        bottom.set_bottom(1)
        border_left_right_header = workbook.add_format({ 'align': 'center',})
        border_left_right_name = workbook.add_format({ 'align': 'left',})
        border_left_right_vals = workbook.add_format({'align': 'right',})
        border_left_right_name.set_right(1)
        border_left_right_name.set_bottom(1)
        border_left_right_name.set_left(1)
        border_left_right_vals.set_right(1)
        border_left_right_vals.set_left(1)
        border_left_right_vals.set_bottom(1)
        border_top_header.set_right(1)
        border_top_header.set_left(1)
        border_top_header.set_top(1)
        border_left_right_header.set_left(1)
        border_left_right_header.set_right(1)
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 15, })
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        header_row_style_right = workbook.add_format({'bold': True, 'align': 'right', 'border': True})
        header_row_style_left = workbook.add_format({'bold': True, 'align': 'left', 'border': True})
        date_range = self.env['date.range'].search([('company_id', '=', data.get('company_id')),('id', '=', data.get('fy_n_id'))])
        company = self.env['res.company'].search([('id', '=', data.get('company_id'))])
        sheet.write(2, 6, company.company_registry)
        sheet.merge_range('B5:G5', 'PIECES ANNEXES A LA', title)
        sheet.merge_range('B6:G6', 'DECLARATION FISCALE', title)
        sheet.merge_range('A8:H8', 'IMPOT SUR LES SOCIETES', title)
        sheet.merge_range('B10:G10', '(Modèle Comptable Normal)', title)
        sheet.write(12, 1, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
        sheet.write(16, 1, 'Raison sociale : ' + str(company.name))
        sheet.write(18, 1, 'Article I.S : ')
        sheet.write(20, 1, 'Adresse : ' + str(company.street))
        sheet.write(23, 4, 'A ……………..........,le ......................')
        sheet.write(26, 5, 'Signature')
        sheet.merge_range('A38:H38', 'CADRE RESERVE A L\'ADMINISTRATION', title)
        sheet.write(41, 1, 'Numéro d\'enregistrement de la déclaration :…………………………………..')
        sheet.write(42, 1, 'Date : ………………………………')
        sheet.write(46, 6, 'Signature')
        sheet.write(56, 1, 'N.B : Les tableaux de 1 à 14 sont conformes aux états prévus par la loi n° 9.88 relatives aux obligations')
        sheet.write(57, 1, 'comptables des commercants promulgées par le Dahir n° 1.92.138 du 3 Joumada II 1413 (15,12,1992)')
        if data.get('boolean') and data.get('boolean') == True :
            if data.get('model_id'):
                model_id = self.env['liass.fiscal'].search([('id','=',data.get('model_id'))])
                for model in model_id.line_ids:
                    # Tableau 1
                    if model.model == 'bilan.active':
                        sheet = workbook.add_worksheet('Actif')
                        actif = self.env['bilan.active'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°1')
                        sheet.write(0, 4, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:F3', 'Bilan Actif', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.set_column(0, 5, 18)
                        sheet.write(row , col, 'ACTIF', header_row_style)
                        sheet.write(row , col+1, 'Brut', header_row_style)
                        sheet.write(row , col+2, 'AMORT ET PROVIS', header_row_style)
                        sheet.write(row , col+3, 'Net', header_row_style)
                        sheet.write(row , col+4, 'Net de Exercice Précédent', header_row_style)
                        row += 1
                        for line in actif.line_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, line.gross,border_left_right_vals)
                            sheet.write(row, col+2, line.amort,border_left_right_vals)
                            sheet.write(row, col+3, line.net,border_left_right_vals)
                            sheet.write(row, col+4, line.prev_net,border_left_right_vals)
                            row += 1
                    if model.model == 'bilan.passive':
                        sheet = workbook.add_worksheet('Passif')
                        passif = self.env['bilan.passive'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°1')
                        sheet.write(0, 2, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:D3', 'Bilan Passif', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.set_column(0, 5, 18)
                        sheet.write(row , col, 'PASSIF', header_row_style)
                        sheet.write(row , col+1, 'EXERCICE', header_row_style)
                        sheet.write(row , col+2, 'EXERCICE PRECEDENT', header_row_style)
                        row += 1
                        for line in passif.line_ids:
                            sheet.write(row, col, line.name,bottom)
                            sheet.write(row, col+1, line.net,bottom)
                            sheet.write(row, col+2, line.prev_net,bottom)
                            row += 1
                    # Tableau 2
                    if model.model == 'charge.profit':
                        sheet = workbook.add_worksheet('CPC')
                        cpc_1 = self.env['charge.profit'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°2')
                        sheet.write(0, 4, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:E3', 'COMPTE DE PRODUITS ET CHARGES (Hors taxes)', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.set_column(0, 5, 18)
                        sheet.write(row , col, 'NATURE', header_row_style)
                        sheet.write(row , col+1, 'PROPRES A L\'EXERCICE', header_row_style)
                        sheet.write(row , col+2, 'CONCERNANT LES EXERCICES PRECEDENTS', header_row_style)
                        sheet.write(row , col+3, 'TOTAUX DE L\'EXERCICE', header_row_style)
                        sheet.write(row , col+4, 'TOTAUX DE L\'EXERCICE PRECEDENT', header_row_style)
                        row += 1
                        for line in cpc_1.line_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, line.current,border_left_right_vals)
                            sheet.write(row, col+2, line.previous,border_left_right_vals)
                            sheet.write(row, col+3, line.net,border_left_right_vals)
                            sheet.write(row, col+4, line.prev_net,border_left_right_vals)
                            row += 1
                    if model.model == 'charge.loss':
                        sheet = workbook.add_worksheet('CPC SUIT')
                        cpc_2 = self.env['charge.loss'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°2')
                        sheet.write(0, 4, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:E3', 'COMPTE DE PRODUITS ET CHARGES (Hors taxes) (Suit)', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.set_column(0, 5, 18)
                        sheet.write(row , col, 'NATURE', header_row_style)
                        sheet.write(row , col+1, 'PROPRES A L\'EXERCICE', header_row_style)
                        sheet.write(row , col+2, 'CONCERNANT LES EXERCICES PRECEDENTS', header_row_style)
                        sheet.write(row , col+3, 'TOTAUX DE L\'EXERCICE', header_row_style)
                        sheet.write(row , col+4, 'TOTAUX DE L\'EXERCICE PRECEDENT', header_row_style)
                        row += 1
                        for line in cpc_2.line_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, line.current,border_left_right_vals)
                            sheet.write(row, col+2, line.previous,border_left_right_vals)
                            sheet.write(row, col+3, line.net,border_left_right_vals)
                            sheet.write(row, col+4, line.prev_net,border_left_right_vals)
                            row += 1
                    # Tableau 3
                    if model.model == 'liasse.passage':
                        sheet = workbook.add_worksheet('Passage')
                        passage = self.env['liasse.passage'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°3')
                        sheet.write(0, 2, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:C3', 'PASSAGE DU RESULTAT NET COMPTABLE AU RESULTAT NET FISCAL', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.set_column(0, 5, 18)
                        sheet.write(row , col, 'INTITULES', header_row_style_left)
                        sheet.write(row , col+1, 'MONTANT', header_row_style_left)
                        sheet.write(row , col+2, 'MONTANT', header_row_style_left)
                        row += 1
                        sheet.write(row , col, 'I. RESULTAT NET COMPTABLE',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '*  Bénéfice net',border_left_right_name)
                        sheet.write(row , col+1, passage.benifice_net_1 ,border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '*  Perte nette',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, passage.perte_nette_1,border_left_right_vals)
                        row += 1
                        sheet.write(row , col, 'II. REINTEGRATIONS FISCALES',border_left_right_name)
                        sheet.write(row , col+1, passage.reintegration_total,border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '1. Courantes',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        for line in passage.re_fy_courante_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, line.montant_1,border_left_right_vals)
                            sheet.write(row, col+2, '',border_left_right_vals)
                            row += 1
                        sheet.write(row , col, '2. Non courantes',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        for line in passage.re_fy_non_courante_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, line.montant_1,border_left_right_vals)
                            sheet.write(row, col+2, '',border_left_right_vals)
                            row += 1
                        sheet.write(row , col, 'III. DEDUCTIONS FISCALES',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, passage.deduction_total,border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '1. Courantes',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        for line in passage.de_fy_courante_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, '',border_left_right_vals)
                            sheet.write(row, col+2, line.montant_1,border_left_right_vals)
                            row += 1
                        sheet.write(row , col, '2. Non courantes',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        for line in passage.de_fy_non_courante_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, '',border_left_right_vals)
                            sheet.write(row, col+2, line.montant_1,border_left_right_vals)
                            row += 1
                        row += 1
                        sheet.write(row , col, 'Total',border_left_right_name)
                        sheet.write(row , col+1, passage.reintegration_total + passage.benifice_net_1,border_left_right_vals)
                        sheet.write(row , col+2, passage.perte_nette_1 + passage.deduction_total,border_left_right_vals)
                        row += 1
                        sheet.write(row , col, 'IV. RESULTAT BRUT FISCAL',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '*  Bénéfice brut si T1> T2 (A)',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, passage.benifice_brut_1,border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '*  Déficit brut fiscal si T2> T1 (B)',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, passage.deficit_brut_1,border_left_right_vals)
                        row += 1
                        sheet.write(row , col, 'V. REPORTS DEFICITAIRES IMPUTES (C) (1)',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, 'CUMUL DES DEFICITES FISCAUX A IMPUTER',border_left_right_name)
                        sheet.write(row , col+1, passage.amortissement,border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '* Exercice N-4',border_left_right_name)
                        sheet.write(row , col+1, passage.exercice_n_4,border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '* Exercice N-3',border_left_right_name)
                        sheet.write(row , col+1, passage.exercice_n_3,border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '* Exercice N-2',border_left_right_name)
                        sheet.write(row , col+1, passage.exercice_n_2,border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '* Exercice N-1',border_left_right_name)
                        sheet.write(row , col+1, passage.exercice_n_1,border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, 'VI . RESULTAT NET FISCAL',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, 'BÈnÈfice net fiscal ( A - C )',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, passage.benifice_net_a_c_1,border_left_right_vals)
                        row += 1
                        sheet.write(row , col, 'ou déficit net fiscal (B)',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, passage.deficit_net_b_1,border_left_right_vals)
                        row += 1
                        sheet.write(row , col, 'VII. CUMUL DES AMORTISSEMENTS FISCALEMENT DIFFERES',border_left_right_name)
                        sheet.write(row , col+1, passage.amortissement_1,border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, 'VIII . CUMUL DES DEFICITES FISCAUX A REPORTER',border_left_right_name)
                        sheet.write(row , col+1, '',border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '* Exercice N-4',border_left_right_name)
                        sheet.write(row , col+1, passage.exercice_n_4_1_c,border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '* Exercice N-3',border_left_right_name)
                        sheet.write(row , col+1, passage.exercice_n_3_1_c,border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '* Exercice N-2',border_left_right_name)
                        sheet.write(row , col+1, passage.exercice_n_2_1_c,border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                        sheet.write(row , col, '* Exercice N-1',border_left_right_name)
                        sheet.write(row , col+1, passage.exercice_n_1_1_c,border_left_right_vals)
                        sheet.write(row , col+2, '',border_left_right_vals)
                        row += 1
                    # Tableau 4
                    if model.model == 'immo.financiere':
                        sheet = workbook.add_worksheet('IMMOBILISATIONS')
                        financiere = self.env['immo.financiere'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°4')
                        sheet.write(0, 8, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:I3', 'TABLEAU DES IMMOBILISATIONS AUTRES QUE FINANCIERES', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.set_column(0, 5, 18)
                        sheet.write(row , col, '',border_top_header )
                        sheet.write(row , col+1, 'MONTANT ', border_top_header)
                        sheet.write(row , col+2, '',top_left )
                        sheet.write(row , col+3, 'AUGMENTATION',top_top )
                        sheet.write(row , col+4, '',top_right )
                        sheet.write(row , col+5, '',top_left )
                        sheet.write(row , col+6, 'DIMINUTION',top_top )
                        sheet.write(row , col+7, '',top_right )
                        sheet.write(row , col+8, 'MONTANT', border_top_header)
                        row += 1
                        sheet.set_column(0, 5, 18)
                        sheet.write(row , col, 'NATURE',border_left_right_header )
                        sheet.write(row , col+1, 'BRUT', border_left_right_header)
                        sheet.write(row , col+2, '',border_top_header )
                        sheet.write(row , col+3, 'PRODUCTION PAR',border_top_header )
                        sheet.write(row , col+4, '',border_top_header )
                        sheet.write(row , col+5, '',border_top_header )
                        sheet.write(row , col+6, '',border_top_header )
                        sheet.write(row , col+7, '',border_top_header )
                        sheet.write(row , col+8, 'BRUT', border_left_right_header)
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, 'DEBUT',border_left_right_header )
                        sheet.write(row , col+2, 'ACQUISITION',border_left_right_header )
                        sheet.write(row , col+3, 'L\'ENTREPRISE', border_left_right_header)
                        sheet.write(row , col+4, 'VIREMENT',border_left_right_header )
                        sheet.write(row , col+5, 'CESSION', border_left_right_header)
                        sheet.write(row , col+6, 'RETRAIT', border_left_right_header)
                        sheet.write(row , col+7, 'VIREMENT', border_left_right_header)
                        sheet.write(row , col+8, 'FIN',border_left_right_header )
                        row += 1
                        sheet.set_column(0, 5, 18)
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, 'EXERCICE', border_left_right_header)
                        sheet.write(row , col+2, '',border_left_right_header )
                        sheet.write(row , col+3, 'POUR ELLE-MEME',border_left_right_header )
                        sheet.write(row , col+4, '',border_left_right_header )
                        sheet.write(row , col+5, '',border_left_right_header )
                        sheet.write(row , col+6, '',border_left_right_header )
                        sheet.write(row , col+7, '',border_left_right_header )
                        sheet.write(row , col+8, 'EXERCICE', border_left_right_header)
                        row += 1
                        for line in financiere.line_ids:
                            if line.code in ['111','222','333']:
                                sheet.write(row, col, line.name ,header_row_style_left )
                                sheet.write(row, col+1, line.montant_start,header_row_style_right )
                                sheet.write(row, col+2, line.augmentation_acquisition,header_row_style_right )
                                sheet.write(row, col+3, line.augmentation_production,header_row_style_right )
                                sheet.write(row, col+4, line.augmentation_transaction,header_row_style_right )
                                sheet.write(row , col+5, line.diminution_cession,header_row_style_right )
                                sheet.write(row , col+6, line.diminution_withdrawal,header_row_style_right )
                                sheet.write(row , col+7, line.diminution_transaction,header_row_style_right )
                                sheet.write(row , col+8, line.montant_end,header_row_style_right )
                            else:
                                sheet.write(row, col, line.name,border_left_right_name)
                                sheet.write(row, col+1, line.montant_start,border_left_right_vals)
                                sheet.write(row, col+2, line.augmentation_acquisition,border_left_right_vals)
                                sheet.write(row, col+3, line.augmentation_production,border_left_right_vals)
                                sheet.write(row, col+4, line.augmentation_transaction,border_left_right_vals)
                                sheet.write(row , col+5, line.diminution_cession,border_left_right_vals)
                                sheet.write(row , col+6, line.diminution_withdrawal,border_left_right_vals)
                                sheet.write(row , col+7, line.diminution_transaction,border_left_right_vals)
                                sheet.write(row , col+8, line.montant_end,border_left_right_vals)
                            row += 1
                    # Tableau 5
                    if model.model == 'esg.tfr':
                        string = ''
                        sheet = workbook.add_worksheet('ESG')
                        esg_tfr = self.env['esg.tfr'].search(domain)
                        esg_caf = self.env['esg.caf'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°5')
                        sheet.write(0, 2, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:C3', 'ETAT DES SOLDES DE GESTION (E.S.G)', title) 
                        sheet.merge_range('A5:C5','I. Tableau de formation des Résultats (T.F.R )',bold)
                        row = 6
                        col = 0
                        # Header row
                        sheet.write(row , col, 'Nature',header_row_style )
                        sheet.write(row , col+1, 'EXERCICE',header_row_style )
                        sheet.write(row , col+2, 'EXERCICE PRECEDENT',header_row_style )
                        row += 1
                        for line in esg_tfr.line_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, line.net,border_left_right_vals)
                            sheet.write(row, col+2, line.prev_net,border_left_right_vals)
                            row += 1
                        row += 1
                        string = 'A'+str(row)+':'+'D'+str(row)
                        sheet.merge_range(string,'II. CAPACITE D\'AUTOFINANCEMENT (C.A.F.) - AUTOFINANCEMENT',bold)
                        row += 1
                        for line in esg_caf.line_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, line.net,border_left_right_vals)
                            sheet.write(row, col+2, line.prev_net,border_left_right_vals)
                            row += 1
                    # Tableau 6 
                    if model.model == 'detail.cpc':
                        sheet = workbook.add_worksheet('Detail CPC')
                        details_cpc = self.env['detail.cpc'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°6')
                        sheet.write(0, 2, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:C3', 'DETAIL DES POSTES DU C.P.C', title) 
                        row = 5
                        col = 0
                        # Header row
                        sheet.write(row , col, 'POSTE',header_row_style )
                        sheet.write(row , col+1, 'EXERCICE',header_row_style )
                        sheet.write(row , col+2, 'EXERCICE PRECEDENT',header_row_style )
                        row += 1
                        for line in details_cpc.line_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, line.net,border_left_right_vals)
                            sheet.write(row, col+2, line.prev_net,border_left_right_vals)
                            row += 1
                        
                    # Tableau 7
                    if model.model == 'credit.bail':
                        sheet = workbook.add_worksheet('Credit Bail')
                        credit_bail = self.env['credit.bail'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°7')
                        sheet.write(0, 10, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:K3', 'TABLEAU DES BIENS EN CREDIT-BAIL', title) 
                        row = 5
                        col = 0
                        # Header row
                        sheet.write(row, col, 'RUBRIQUES',header_row_style)
                        sheet.write(row, col+1, 'DATE DE ECHEANCE',header_row_style)
                        sheet.write(row, col+2, 'DUREE DU CONTRAT EN MOIS',header_row_style)
                        sheet.write(row, col+3, 'VALEUR ESTIMEE',header_row_style)
                        sheet.write(row, col+4, 'DUREE THEORIQUE',header_row_style)
                        sheet.write(row, col+5, 'CUMUL DES EXERCICES PRECEDENTS DES REDEVANCES',header_row_style)
                        sheet.write(row, col+6, 'MONTANT DE EXERCICES DES REDEVANCES',header_row_style)
                        sheet.write(row, col+7, 'A MOINS D\'UN AN',header_row_style)
                        sheet.write(row, col+8, 'A PLUS D\'UN AN',header_row_style)
                        sheet.write(row, col+9, 'PRIX D\'ACHAT RESIDUEL',header_row_style)
                        sheet.write(row, col+10, 'OBSERVATIONS',header_row_style)
                        row += 1
                        for line in credit_bail.credit_bail_line_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, line.date_premiere_echeance,border_left_right_name)
                            sheet.write(row, col+2, line.duuree_contrat,border_left_right_vals)
                            sheet.write(row, col+3, line.valeur_estimee,border_left_right_vals)
                            sheet.write(row, col+4, line.duuree_theorique,border_left_right_vals)
                            sheet.write(row, col+5, line.cumul_redevance,border_left_right_vals)
                            sheet.write(row, col+6, line.montant_redevance,border_left_right_vals)
                            sheet.write(row, col+7, line.redevance_restant_moins,border_left_right_vals)
                            sheet.write(row, col+8, line.redevance_restant_plus,border_left_right_vals)
                            sheet.write(row, col+9, line.prix_achat_fin_contrat,border_left_right_vals)
                            sheet.write(row, col+10, line.observations,border_left_right_name)
                            row += 1
                        if not credit_bail.credit_bail_line_ids:
                            for i in range(20):
                                sheet.write(row, col, '',bottom )
                                sheet.write(row, col+1, '',bottom)
                                sheet.write(row, col+2, '',bottom)
                                sheet.write(row, col+3, '',bottom)
                                sheet.write(row, col+4, '',bottom)
                                sheet.write(row, col+5, '',bottom)
                                sheet.write(row, col+6, '',bottom)
                                sheet.write(row, col+7, '',bottom)
                                sheet.write(row, col+8, '',bottom)
                                sheet.write(row, col+9, '',bottom)
                                sheet.write(row, col+10, '',bottom)
                                row += 1
                    if model.model == 'immo.amortissements':
                        sheet = workbook.add_worksheet('AMORTISSEMENT')
                        financiere = self.env['immo.amortissements'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°8')
                        sheet.write(0, 4, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:E3', 'TABLEAU DES AMORTISSEMENTS', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.set_column(0, 5, 18)
                        sheet.write(row , col, '',border_top_header )
                        sheet.write(row , col+1, 'CUMUL', border_top_header)
                        sheet.write(row , col+2, 'DOTATION DE ',border_top_header )
                        sheet.write(row , col+3, 'AMORTISSEMENTS',border_top_header )
                        sheet.write(row , col+4, 'CUMUL',border_top_header )
                        row += 1
                        sheet.write(row , col, 'NATURE',border_left_right_header )
                        sheet.write(row , col+1, 'D\'AMORTISSEMENT', border_left_right_header)
                        sheet.write(row , col+2, 'L\'EXERCICE',border_left_right_header )
                        sheet.write(row , col+3, 'SUR IMMOBILISATIONS',border_left_right_header )
                        sheet.write(row , col+4, 'D\'AMORTISSEMENT',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, 'DEBUT EXERCICE', border_left_right_header)
                        sheet.write(row , col+2, '',border_left_right_header )
                        sheet.write(row , col+3, 'SORTIES',border_left_right_header )
                        sheet.write(row , col+4, 'FIN EXERCICE',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',bottom )
                        sheet.write(row , col+1, '1', bottom)
                        sheet.write(row , col+2, '2 ',bottom )
                        sheet.write(row , col+3, '3',bottom )
                        sheet.write(row , col+4, '4=1+2-3',bottom )
                        row += 1
                        for line in financiere.line_ids:
                            if line.code in ['111','222','333']:
                                sheet.write(row, col, line.name ,header_row_style_left )
                                sheet.write(row, col+1, line.debut_exercice,header_row_style_right )
                                sheet.write(row, col+2, line.dotation_exercice,header_row_style_right )
                                sheet.write(row, col+3, line.amortissement_sortie,header_row_style_right )
                                sheet.write(row, col+4, line.cumule_amortissement,header_row_style_right )
                            else:
                                sheet.write(row, col, line.name,border_left_right_name)
                                sheet.write(row, col+1, line.debut_exercice,border_left_right_vals)
                                sheet.write(row, col+2, line.dotation_exercice,border_left_right_vals)
                                sheet.write(row, col+3, line.amortissement_sortie,border_left_right_vals)
                                sheet.write(row, col+4, line.cumule_amortissement,border_left_right_vals)
                            row += 1
                    if model.model == 'provisions':
                        sheet = workbook.add_worksheet('PROVISIONS')
                        financiere = self.env['provisions'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°9')
                        sheet.write(0, 8, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:I3', 'TABLEAU DES PROVISIONS', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.write(row , col, 'NATURE',border_top_header )
                        sheet.write(row , col+1, 'MONTANT', border_top_header)
                        sheet.write(row , col+2, '',border_top_header )
                        sheet.write(row , col+3, '',border_top_header )
                        sheet.write(row , col+4, '',border_top_header )
                        sheet.write(row , col+5, '',border_top_header )
                        sheet.write(row , col+6, '',border_top_header )
                        sheet.write(row , col+7, '',border_top_header )
                        sheet.write(row , col+8, 'MONTANT',border_top_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, 'DEBUT', border_left_right_header)
                        sheet.write(row , col+2, '',border_left_right_header )
                        sheet.write(row , col+3, 'DOTATIONS',border_left_right_header )
                        sheet.write(row , col+4, '',border_left_right_header )
                        sheet.write(row , col+5, '',border_left_right_header )
                        sheet.write(row , col+6, 'REPRISES',border_left_right_header )
                        sheet.write(row , col+7, '',border_left_right_header )
                        sheet.write(row , col+8, 'FIN',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',bottom )
                        sheet.write(row , col+1, 'EXERCICE', bottom)
                        sheet.write(row , col+2, 'EXPLOITATION ',bottom )
                        sheet.write(row , col+3, 'FINANCIERES',bottom )
                        sheet.write(row , col+4, 'NON COURANTES',bottom )
                        sheet.write(row , col+5, 'EXPLOITATION',bottom )
                        sheet.write(row , col+6, 'FINANCIERES',bottom )
                        sheet.write(row , col+7, 'NON COURANTES',bottom )
                        sheet.write(row , col+8, 'EXERCICE',bottom )
                        row += 1
                        for line in financiere.provisions_line_ids:
                            if line.name == '1. Provisions pour dépréciation de l\'actif immobilisé':
                                sheet.write(row, col, line.name ,border_left_right_name )
                                sheet.write(row, col+1, line.montant_debut,border_left_right_vals )
                                sheet.write(row, col+2, line.dotation_exploitation,border_left_right_vals )
                                sheet.write(row, col+3, line.dotation_financiere,border_left_right_vals )
                                sheet.write(row, col+4, line.dotation_non_courante,border_left_right_vals )
                                sheet.write(row, col+5, line.reprises_exploitation,border_left_right_vals )
                                sheet.write(row, col+6, line.reprises_financiere,border_left_right_vals )
                                sheet.write(row, col+7, line.reprises_non_courante,border_left_right_vals )
                                sheet.write(row, col+8, line.montant_fin,border_left_right_vals )
                            elif line.name in ['SOUS TOTAL (A)', 'SOUS TOTAL (B)','TOTAL (A+B)']:
                                sheet.write(row, col, line.name ,header_row_style_left )
                                sheet.write(row, col+1, line.montant_debut,header_row_style_right )
                                sheet.write(row, col+2, line.dotation_exploitation,header_row_style_right )
                                sheet.write(row, col+3, line.dotation_financiere,header_row_style_right )
                                sheet.write(row, col+4, line.dotation_non_courante,header_row_style_right )
                                sheet.write(row, col+5, line.reprises_exploitation,header_row_style_right )
                                sheet.write(row, col+6, line.reprises_financiere,header_row_style_right )
                                sheet.write(row, col+7, line.reprises_non_courante,header_row_style_right )
                                sheet.write(row, col+8, line.montant_fin,header_row_style_right )
                            else:
                                sheet.write(row, col, line.name ,border_left_right_name )
                                sheet.write(row, col+1, line.montant_debut,border_left_right_vals )
                                sheet.write(row, col+2, line.dotation_exploitation,border_left_right_vals )
                                sheet.write(row, col+3, line.dotation_financiere,border_left_right_vals )
                                sheet.write(row, col+4, line.dotation_non_courante,border_left_right_vals )
                                sheet.write(row, col+5, line.reprises_exploitation,border_left_right_vals )
                                sheet.write(row, col+6, line.reprises_financiere,border_left_right_vals )
                                sheet.write(row, col+7, line.reprises_non_courante,border_left_right_vals )
                                sheet.write(row, col+8, line.montant_fin,border_left_right_vals )
                            row += 1
                    if model.model == 'immo.immobilisation':
                        sheet = workbook.add_worksheet('Cession')
                        cession = self.env['immo.immobilisation'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°10')
                        sheet.write(0, 7, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:H3', 'TABLEAU DES PLUS OU MOINS VALUES SUR CESSION OU RETRAITS D\'IMMOBILISATIONS', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.write(row , col, 'DATE DE CESSION',border_top_header )
                        sheet.write(row , col+1, 'COMPTE', border_top_header)
                        sheet.write(row , col+2, 'MONTANT',border_top_header )
                        sheet.write(row , col+3, 'AMORTISSEMENTS',border_top_header )
                        sheet.write(row , col+4, 'VALEUR NETTE',border_top_header )
                        sheet.write(row , col+5, 'PRODUIT DE',border_top_header )
                        sheet.write(row , col+6, 'PLUS',border_top_header )
                        sheet.write(row , col+7, 'MOINS',border_top_header )
                        row += 1
                        sheet.write(row , col, 'OU DE RETRAIT',bottom )
                        sheet.write(row , col+1, 'PRINCIPAL', bottom)
                        sheet.write(row , col+2, 'BRUT',bottom )
                        sheet.write(row , col+3, 'CUMULES',bottom )
                        sheet.write(row , col+4, 'D\'AMORTISSEMENTS',bottom )
                        sheet.write(row , col+5, 'CESSION',bottom )
                        sheet.write(row , col+6, 'VALUES',bottom )
                        sheet.write(row , col+7, 'VALUES',bottom )
                        row += 1
                        for line in cession.line_ids:
                            sheet.write(row, col, line.date_in ,border_left_right_name )
                            sheet.write(row, col+1, line.code,border_left_right_vals )
                            sheet.write(row, col+2, line.montant_brut,border_left_right_vals )
                            sheet.write(row, col+3, line.amortissement_cumul,border_left_right_vals )
                            sheet.write(row, col+4, line.amortissement_net,border_left_right_vals )
                            sheet.write(row, col+5, line.cession,border_left_right_vals )
                            sheet.write(row, col+6, line.plus_value,border_left_right_vals )
                            sheet.write(row, col+7, line.minece_value,border_left_right_vals )
                            row += 1
                        if not cession.line_ids:
                            for i in range(20):
                                sheet.write(row, col, '',bottom )
                                sheet.write(row, col+1, '',bottom )
                                sheet.write(row, col+2,'',bottom )
                                sheet.write(row, col+3, '',bottom )
                                sheet.write(row, col+4, '',bottom )
                                sheet.write(row, col+5, '',bottom )
                                sheet.write(row, col+6, '',bottom )
                                sheet.write(row, col+7, '',bottom )
                                row += 1
                    if model.model == 'titre.participation':
                        sheet = workbook.add_worksheet('Participation')
                        cession = self.env['titre.participation'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°11')
                        sheet.write(0, 10, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:K3', 'TABLEAU DES TITRES DE PARTICIPATION', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.write(row , col, 'RAISON SOCIALE',border_top_header )
                        sheet.write(row , col+1, '', border_top_header)
                        sheet.write(row , col+2, 'SECTEUR',border_top_header )
                        sheet.write(row , col+3, 'CAPITAL',border_top_header )
                        sheet.write(row , col+4, 'PARTICIPATION',border_top_header )
                        sheet.write(row , col+5, 'PRIX',border_top_header )
                        sheet.write(row , col+6, 'VALEUR',border_top_header )
                        sheet.write(row , col+7, 'EXTRAIT DES',top_left )
                        sheet.write(row , col+8, 'DERNIERS',top_top )
                        sheet.write(row , col+9, 'ETATS DE',top_right )
                        sheet.write(row , col+10, 'PRODUITS',border_top_header )
                        row += 1
                        sheet.write(row , col, 'DE LA',border_left_right_header )
                        sheet.write(row , col+1, '', border_left_right_header)
                        sheet.write(row , col+2, 'D\'ACTIVITE',border_left_right_header )
                        sheet.write(row , col+3, 'SOCIAL',border_left_right_header )
                        sheet.write(row , col+4, 'AU CAPITAL',border_left_right_header )
                        sheet.write(row , col+5, 'D\'ACQUISITION',border_left_right_header )
                        sheet.write(row , col+6, 'COMPTABLE',border_left_right_header )
                        sheet.write(row , col+7, 'SYNTHESE DE',top_left )
                        sheet.write(row , col+8, 'LA SOCIETE',top_top )
                        sheet.write(row , col+9, 'EMETTRICE',top_right )
                        sheet.write(row , col+10, 'INSCRITS',border_left_right_header )
                        row += 1
                        sheet.write(row , col, 'SOCIETE EMETTRICE',border_left_right_header )
                        sheet.write(row , col+1, 'N° IF', border_left_right_header)
                        sheet.write(row , col+2, '',border_left_right_header )
                        sheet.write(row , col+3, '',border_left_right_header )
                        sheet.write(row , col+4, '%',border_left_right_header )
                        sheet.write(row , col+5, 'GLOBAL',border_left_right_header )
                        sheet.write(row , col+6, 'NETTE',border_left_right_header )
                        sheet.write(row , col+7, 'DATE DE',border_top_header )
                        sheet.write(row , col+8, 'SITUATION',border_top_header )
                        sheet.write(row , col+9, 'RESULTAT',border_top_header )
                        sheet.write(row , col+10, 'AU C.P.C DE',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, '', border_left_right_header)
                        sheet.write(row , col+2, '',border_left_right_header )
                        sheet.write(row , col+3, '',border_left_right_header )
                        sheet.write(row , col+4, '',border_left_right_header )
                        sheet.write(row , col+5, '',border_left_right_header )
                        sheet.write(row , col+6, '',border_left_right_header )
                        sheet.write(row , col+7, 'CLOTURE',border_left_right_header )
                        sheet.write(row , col+8, 'NETTE',border_left_right_header )
                        sheet.write(row , col+9, 'NET',border_left_right_header )
                        sheet.write(row , col+10, 'L\'EXERCICE',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',bottom )
                        sheet.write(row , col+1, '', bottom)
                        sheet.write(row , col+2, '1',bottom )
                        sheet.write(row , col+3, '2',bottom )
                        sheet.write(row , col+4, '3',bottom )
                        sheet.write(row , col+5, '4',bottom )
                        sheet.write(row , col+6, '5',bottom )
                        sheet.write(row , col+7, '6',bottom )
                        sheet.write(row , col+8, '7',bottom )
                        sheet.write(row , col+9, '8',bottom )
                        sheet.write(row , col+10, '9',bottom )
                        row += 1
                        for line in cession.titre_participation_line_ids:
                            sheet.write(row, col, line.name ,border_left_right_name )
                            sheet.write(row, col+1, line.code,border_left_right_vals )
                            sheet.write(row, col+2, line.secteur_activite,border_left_right_vals )
                            sheet.write(row, col+3, line.capital_social,border_left_right_vals )
                            sheet.write(row, col+4, line.participation_capital,border_left_right_vals )
                            sheet.write(row, col+5, line.prix_acquisition,border_left_right_vals )
                            sheet.write(row, col+6, line.valeur_comptable_nette,border_left_right_vals )
                            sheet.write(row, col+7, line.date_cloture,border_left_right_vals )
                            sheet.write(row, col+8, line.situation_nette,border_left_right_vals )
                            sheet.write(row, col+9, line.resultat_net,border_left_right_vals )
                            sheet.write(row, col+10, line.produits_inscrits,border_left_right_vals )
                            row += 1
                        if not cession.titre_participation_line_ids:
                            for i in range(20):
                                sheet.write(row, col, '',bottom )
                                sheet.write(row, col+1, '',bottom )
                                sheet.write(row, col+2,'',bottom )
                                sheet.write(row, col+3, '',bottom )
                                sheet.write(row, col+4, '',bottom )
                                sheet.write(row, col+5, '',bottom )
                                sheet.write(row, col+6, '',bottom )
                                sheet.write(row, col+7, '',bottom )
                                sheet.write(row, col+8, '',bottom )
                                sheet.write(row, col+9, '',bottom )
                                sheet.write(row, col+10, '',bottom )
                                row += 1
                    if model.model == 'osi.tva':
                        sheet = workbook.add_worksheet('Tva')
                        cession = self.env['osi.tva'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°12')
                        sheet.write(0, 4, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:E3', 'DETAIL DE LA TAXE SUR LA VALEUR AJOUTEE', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.write(row , col, '',border_top_header )
                        sheet.write(row , col+1, 'SOLDE AU', border_top_header)
                        sheet.write(row , col+2, 'OPERATIONS',border_top_header )
                        sheet.write(row , col+3, 'DECLARATIONS',border_top_header )
                        sheet.write(row , col+4, 'SOLDE',border_top_header )
                        row += 1
                        sheet.write(row , col, 'NATURE',border_left_right_header )
                        sheet.write(row , col+1, 'DEBUT DE', border_left_right_header)
                        sheet.write(row , col+2, 'COMPTABLES DE',border_left_right_header )
                        sheet.write(row , col+3, 'T.V.A DE',border_left_right_header )
                        sheet.write(row , col+4, 'FIN DE',border_left_right_header )
                        row += 1
                        sheet.write(row , col, ' ',border_left_right_header )
                        sheet.write(row , col+1, 'L\'EXERCICE', border_left_right_header)
                        sheet.write(row , col+2, 'L\'EXERCICE',border_left_right_header )
                        sheet.write(row , col+3, 'L\'EXERCICE',border_left_right_header )
                        sheet.write(row , col+4, 'L\'EXERCICE',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',bottom )
                        sheet.write(row , col+1, '1', bottom)
                        sheet.write(row , col+2, '2',bottom )
                        sheet.write(row , col+3, '3',bottom )
                        sheet.write(row , col+4, '4 = 1 + 2 - 3',bottom )
                        row += 1
                        for line in cession.line_ids:
                            sheet.write(row, col, line.name ,border_left_right_name )
                            sheet.write(row, col+1, line.start_solde,border_left_right_vals )
                            sheet.write(row, col+2, line.operation_solde,border_left_right_vals )
                            sheet.write(row, col+3, line.declaration_solde,border_left_right_vals )
                            sheet.write(row, col+4, line.end_solde,border_left_right_vals )
                            row += 1
                    
                    if model.model == 'repartition.capital.social':
                        sheet = workbook.add_worksheet('Capital sociale')
                        cession = self.env['repartition.capital.social'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°13')
                        sheet.write(0, 11, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:L3', 'ETAT DE REPARTITION DU CAPITAL SOCIAL', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.write(row , col, 'NOM ET PRENOM',border_top_header )
                        sheet.write(row , col+1, 'RAISON SOCIAL', border_top_header)
                        sheet.write(row , col+2, ' ',border_top_header )
                        
                        sheet.write(row , col+3, ' ',border_top_header )
                        sheet.write(row , col+4, ' ',border_top_header )
                        sheet.write(row , col+5, ' ',border_top_header )
                        sheet.write(row , col+6, 'NOMBRE',top_left )
                        sheet.write(row , col+7, 'TITRES',top_right )
                        sheet.write(row , col+8, 'VALEUR',border_top_header )
                        sheet.write(row , col+9, 'MONTANT',top_left )
                        sheet.write(row , col+10, 'DU',top_top )
                        sheet.write(row , col+11, 'CAPITAL',top_right )
                        row += 1
                        sheet.write(row , col, 'DES PRINCIPAUX',border_left_right_header )
                        sheet.write(row , col+1, 'DES PRINCIPAUX', border_left_right_header)
                        sheet.write(row , col+2, 'N° IF',border_left_right_header )
                        sheet.write(row , col+3, 'N° CNI',border_left_right_header )
                        sheet.write(row , col+4, 'N° CE',border_left_right_header )
                        sheet.write(row , col+5, 'ADRESSE',border_left_right_header )
                        sheet.write(row , col+6, 'N-1',border_left_right_header )
                        sheet.write(row , col+7, 'N',border_top_header )
                        sheet.write(row , col+8, 'NOMINALE',border_top_header )
                        sheet.write(row , col+9, 'SOUSCRIT',border_top_header )
                        sheet.write(row , col+10, 'APPELE',border_top_header )
                        sheet.write(row , col+11, 'LIBERE',border_top_header )
                        row += 1
                        sheet.write(row , col, 'ASSOCIES (1)',border_left_right_header )
                        sheet.write(row , col+1, 'ASSOCIES (1)', border_left_right_header)
                        sheet.write(row , col+2, '',border_left_right_header )
                        sheet.write(row , col+3, '',border_left_right_header )
                        sheet.write(row , col+4, '',border_left_right_header )
                        sheet.write(row , col+5, '',border_left_right_header )
                        sheet.write(row , col+6, '',border_left_right_header )
                        sheet.write(row , col+7, '',border_top_header )
                        sheet.write(row , col+8, '',border_top_header )
                        sheet.write(row , col+9, '',border_top_header )
                        sheet.write(row , col+10, '',border_left_right_header )
                        sheet.write(row , col+11, '',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '1',bottom )
                        sheet.write(row , col+1, '2', bottom)
                        sheet.write(row , col+2, '3',bottom )
                        sheet.write(row , col+3, '4',bottom )
                        sheet.write(row , col+4, '5',bottom )
                        sheet.write(row , col+5, '6',bottom )
                        sheet.write(row , col+6, '7',bottom )
                        sheet.write(row , col+7, '8',bottom )
                        sheet.write(row , col+8, '9',bottom )
                        sheet.write(row , col+9, '10',bottom )
                        sheet.write(row , col+10, '11',bottom )
                        sheet.write(row , col+11, '12',bottom )
                        row += 1
                        for line in cession.repartition_capital_social_line_ids:
                            sheet.write(row, col, line.name ,border_left_right_name )
                            sheet.write(row, col+1, line.raison_social,border_left_right_vals )
                            sheet.write(row, col+2, line.n_if,border_left_right_vals )
                            sheet.write(row, col+3, line.n_cin,border_left_right_vals )
                            sheet.write(row, col+4, line.n_etr,border_left_right_vals )
                            sheet.write(row, col+5, line.adresse,border_left_right_vals )
                            sheet.write(row, col+6, line.nbre_titre_exe_prec,border_left_right_vals )
                            sheet.write(row, col+7, line.nbre_titre_exe_actuel,border_left_right_vals )
                            sheet.write(row, col+8, line.valeur_nominal,border_left_right_vals )
                            sheet.write(row, col+9, line.montant_capital_souscrit,border_left_right_vals )
                            sheet.write(row, col+10, line.montant_capital_appele,border_left_right_vals )
                            sheet.write(row, col+11, line.montant_capital_libere,border_left_right_vals )
                            row += 1
                        if not cession.repartition_capital_social_line_ids:
                            for i in range(20):
                                sheet.write(row, col, '',bottom )
                                sheet.write(row, col+1, '',bottom )
                                sheet.write(row, col+2,'',bottom )
                                sheet.write(row, col+3, '',bottom )
                                sheet.write(row, col+4, '',bottom )
                                sheet.write(row, col+5, '',bottom )
                                sheet.write(row, col+6, '',bottom )
                                sheet.write(row, col+7, '',bottom )
                                sheet.write(row, col+8, '',bottom )
                                sheet.write(row, col+9, '',bottom )
                                sheet.write(row, col+10, '',bottom )
                                sheet.write(row, col+11, '',bottom )
                                row += 1
                    if model.model == 'affectation.resultats.intervenue':
                        sheet = workbook.add_worksheet('affectation de resultats')
                        cession = self.env['affectation.resultats.intervenue'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°14')
                        sheet.write(0, 3, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:D3', 'TABLEAU D\'AFFECTATION DES RESULTATS INTERVENUE AU COURS DE L\'EXERCICE', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.write(row , col, '',border_top_header )
                        sheet.write(row , col+1, 'MONTANT', border_top_header)
                        sheet.write(row , col+2, ' ',border_top_header )
                        sheet.write(row , col+3, 'MONTANT',border_top_header )
                        row += 1
                        sheet.write(row , col, '',bottom )
                        sheet.write(row , col+1, '', bottom)
                        sheet.write(row , col+2, '',bottom )
                        sheet.write(row , col+3, '',bottom )
                        row += 1
                        for line in cession.affectation_resultats_intervenue_line1_ids:
                            sheet.write(row, col, line.name ,border_left_right_name )
                            sheet.write(row, col+1, line.montant,border_left_right_vals )
                            row += 1
                        row = 7 
                        for line in cession.affectation_resultats_intervenue_line1_ids:
                            sheet.write(row, col+2, line.name ,border_left_right_name )
                            sheet.write(row, col+3, line.montant,border_left_right_vals )
                            row += 1
                    if model.model == 'calcul.impot':
                        sheet = workbook.add_worksheet('Impot')
                        cession = self.env['calcul.impot'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°15')
                        sheet.write(0, 1, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:B3', 'ETAT POUR LE CALCUL DE L\'IMPOT SUR LES SOCIETES - ENTREPRISES ENCOURAGEES', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.write(row , col, '', border_top_header)
                        sheet.write(row , col+1, '',border_top_header )
                        row += 1
                        sheet.write(row , col, 'NATURE DES PRODUITS', border_left_right_header)
                        sheet.write(row , col+1, 'MONTANT',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '', border_left_right_header)
                        sheet.write(row , col+1, '',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',bottom )
                        sheet.write(row , col+1, '', bottom)
                        row += 1
                        for line in cession.calcul_impot_line_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, line.montant,border_left_right_vals )
                            row += 1
                    if model.model == 'immo.dotation':
                        sheet = workbook.add_worksheet('Dotation')
                        cession = self.env['immo.dotation'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°16')
                        sheet.write(0, 10, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:K3', 'ETAT DE DOTATIONS AUX AMORTISSEMENTS', title)
                        sheet.merge_range('A4:K4', 'RELATIFS AUX IMMOBILISATIONS', title)
                        # to be continued
                        row = 6
                        col = 0
                        # Header row
                        sheet.write(row , col, '',border_top_header )
                        sheet.write(row , col+1, '', border_top_header)
                        sheet.write(row , col+2, 'Valeur à ',top_right )
                        sheet.write(row , col+3, ' amortir',top_left )
                        sheet.write(row , col+4, '',border_top_header )
                        sheet.write(row , col+5, 'Amortissements ',top_right )
                        sheet.write(row , col+6, 'déduits du',top_top )
                        sheet.write(row , col+7, '',top_left )
                        sheet.write(row , col+8, '',border_top_header )
                        sheet.write(row , col+9, '',border_top_header )
                        sheet.write(row , col+10, '',border_top_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, '', border_left_right_header)
                        sheet.write(row , col+2, 'PRIX',border_top_header )
                        sheet.write(row , col+3, 'VALEUR',border_top_header )
                        sheet.write(row , col+4, '',border_left_right_header )
                        sheet.write(row , col+5, 'bénéfice ',top_right )
                        sheet.write(row , col+6, 'brut de',top_top )
                        sheet.write(row , col+7, ' l\'exercice',top_left )
                        sheet.write(row , col+8, ' ',border_left_right_header )
                        sheet.write(row , col+9, ' ',border_left_right_header )
                        sheet.write(row , col+10, ' ',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, 'DATE', border_left_right_header)
                        sheet.write(row , col+2, ' D\'ACQUISITION',border_left_right_header )
                        sheet.write(row , col+3, 'COMPTABLE',border_left_right_header )
                        sheet.write(row , col+4, 'AMORTISSEM.',border_left_right_header )
                        sheet.write(row , col+5, 'TAUX',border_left_right_header )
                        sheet.write(row , col+6, 'DUREE',border_left_right_header )
                        sheet.write(row , col+7, 'AMORTISSEM.',border_top_header )
                        sheet.write(row , col+8, 'TOTAL DES',border_top_header )
                        sheet.write(row , col+9, 'OBSERVATION',border_top_header )
                        sheet.write(row , col+10, 'NATURE',border_top_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, 'ENTREE', border_left_right_header)
                        sheet.write(row , col+2, '(2)',border_left_right_header )
                        sheet.write(row , col+3, 'APRES',border_left_right_header )
                        sheet.write(row , col+4, 'ANTERIEURS',border_left_right_header )
                        sheet.write(row , col+5, '',border_left_right_header )
                        sheet.write(row , col+6, '(4)',border_left_right_header )
                        sheet.write(row , col+7, 'NORMAUX OU',border_left_right_header )
                        sheet.write(row , col+8, 'AMORTISSEM.',border_left_right_header )
                        sheet.write(row , col+9, '(5)',border_left_right_header )
                        sheet.write(row , col+10, '',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, '(1)', border_left_right_header)
                        sheet.write(row , col+2, ' ',border_left_right_header )
                        sheet.write(row , col+3, 'REEVALUATION',border_left_right_header )
                        sheet.write(row , col+4, '(3)',border_left_right_header )
                        sheet.write(row , col+5, '',border_left_right_header )
                        sheet.write(row , col+6, '',border_left_right_header )
                        sheet.write(row , col+7, 'ACCELERES',border_left_right_header )
                        sheet.write(row , col+8, 'A LA FIN DE',border_left_right_header )
                        sheet.write(row , col+9, ' ',border_left_right_header )
                        sheet.write(row , col+10, '',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, '', border_left_right_header)
                        sheet.write(row , col+2, ' ',border_left_right_header )
                        sheet.write(row , col+3, ' ',border_left_right_header )
                        sheet.write(row , col+4, ' ',border_left_right_header )
                        sheet.write(row , col+5, '',border_left_right_header )
                        sheet.write(row , col+6, ' ',border_left_right_header )
                        sheet.write(row , col+7, 'DE L\'EXERCICE',border_left_right_header )
                        sheet.write(row , col+8, 'L\'EXERCICE ',border_left_right_header )
                        sheet.write(row , col+9, ' ',border_left_right_header )
                        sheet.write(row , col+10, '',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, '', border_left_right_header)
                        sheet.write(row , col+2, ' ',border_left_right_header )
                        sheet.write(row , col+3, ' ',border_left_right_header )
                        sheet.write(row , col+4, ' ',border_left_right_header )
                        sheet.write(row , col+5, '',border_left_right_header )
                        sheet.write(row , col+6, ' ',border_left_right_header )
                        sheet.write(row , col+7, '',border_left_right_header )
                        sheet.write(row , col+8, '(col.4 + col.7)',border_left_right_header )
                        sheet.write(row , col+9, ' ',border_left_right_header )
                        sheet.write(row , col+10, '',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',bottom )
                        sheet.write(row , col+1, '1', bottom)
                        sheet.write(row , col+2, '2',bottom )
                        sheet.write(row , col+3, '3',bottom )
                        sheet.write(row , col+4, '4',bottom )
                        sheet.write(row , col+5, '5',bottom )
                        sheet.write(row , col+6, '6',bottom )
                        sheet.write(row , col+7, '7',bottom )
                        sheet.write(row , col+8, '8',bottom )
                        sheet.write(row , col+9, '9',bottom )
                        sheet.write(row , col+10, '',bottom )
                        row += 1
                        i=0
                        for line in cession.line_ids:
                            i+=1
                            sheet.write(row, col, i , border_left_right_name )
                            sheet.write(row, col+1, line.date_in,border_left_right_name )
                            sheet.write(row, col+2, line.acquisition_price,border_left_right_vals )
                            sheet.write(row, col+3, line.revaluation_value,border_left_right_vals )
                            sheet.write(row, col+4, line.amortissement_internal,border_left_right_vals )
                            sheet.write(row, col+5, line.taux,border_left_right_vals )
                            sheet.write(row, col+6, line.duration,border_left_right_vals )
                            sheet.write(row, col+7, line.normal_amortissement,border_left_right_vals )
                            sheet.write(row, col+8, line.end_amortissement,border_left_right_vals )
                            sheet.write(row, col+9, line.observation,border_left_right_name )
                            sheet.write(row, col+10, line.name,border_left_right_name )
                            row += 1
                    if model.model == 'plus.values.fusion':
                        sheet = workbook.add_worksheet('Fusion')
                        cession = self.env['plus.values.fusion'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°17')
                        sheet.write(0, 11, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:J3', ' ETAT DES PLUS-VALUES CONSTATEES EN CAS DE  FUSIONS', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.write(row , col, '',border_top_header )
                        sheet.write(row , col+1, '', border_top_header)
                        sheet.write(row , col+2, ' ',border_top_header )
                        sheet.write(row , col+3, ' ',border_top_header )
                        sheet.write(row , col+4, '',border_top_header )
                        sheet.write(row , col+5, 'FRACTION DE ',border_top_header )
                        sheet.write(row , col+6, 'FRACTION DE',top_left )
                        sheet.write(row , col+7, '',top_right )
                        sheet.write(row , col+8, '',border_top_header )
                        sheet.write(row , col+9, '',top_left )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, '', border_left_right_header)
                        sheet.write(row , col+2, '',border_left_right_header )
                        sheet.write(row , col+3, '',border_left_right_header )
                        sheet.write(row , col+4, '',border_left_right_header )
                        sheet.write(row , col+5, 'LA PLUS-VALUE',border_left_right_header )
                        sheet.write(row , col+6, 'LA PLUS-VALUE',border_left_right_header )
                        sheet.write(row , col+7, ' ',border_top_header )
                        sheet.write(row , col+8, ' ',border_top_header )
                        sheet.write(row , col+9, ' ',border_top_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, 'ELEMENTS', border_left_right_header)
                        sheet.write(row , col+2, 'VALEUR',border_left_right_header )
                        sheet.write(row , col+3, 'VALEUR',border_left_right_header )
                        sheet.write(row , col+4, 'PLUS-VALUES',border_left_right_header )
                        sheet.write(row , col+5, 'RAPPORTEE AUX',border_left_right_header )
                        sheet.write(row , col+6, 'RAPPORTEE A',border_left_right_header )
                        sheet.write(row , col+7, 'CUMUL DES',border_top_header )
                        sheet.write(row , col+8, 'SOLDE DES',border_top_header )
                        sheet.write(row , col+9, 'OBSERVATION',border_top_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, '', border_left_right_header)
                        sheet.write(row , col+2, ' ',border_left_right_header )
                        sheet.write(row , col+3, 'COMPTABLE',border_left_right_header )
                        sheet.write(row , col+4, 'ET DIFFEREE',border_left_right_header )
                        sheet.write(row , col+5, 'ANTERIEURS',border_left_right_header )
                        sheet.write(row , col+6, 'ACTUEL',border_left_right_header )
                        sheet.write(row , col+7, 'RAPPORTEES',border_left_right_header )
                        sheet.write(row , col+8, 'NON-IMPUTEES',border_left_right_header )
                        sheet.write(row , col+9, '',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, '', border_left_right_header)
                        sheet.write(row , col+2, ' ',border_left_right_header )
                        sheet.write(row , col+3, ' ',border_left_right_header )
                        sheet.write(row , col+4, ' ',border_left_right_header )
                        sheet.write(row , col+5, '(CUMUL) (2)',border_left_right_header )
                        sheet.write(row , col+6, ' ',border_left_right_header )
                        sheet.write(row , col+7, ' ',border_left_right_header )
                        sheet.write(row , col+8, ' ',border_left_right_header )
                        sheet.write(row , col+9, '',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',bottom )
                        sheet.write(row , col+1, '', bottom)
                        sheet.write(row , col+2, ' ',bottom )
                        sheet.write(row , col+3, ' ',bottom )
                        sheet.write(row , col+4, ' ',bottom )
                        sheet.write(row , col+5, ' ',bottom )
                        sheet.write(row , col+6, ' ',bottom )
                        sheet.write(row , col+7, '  ',bottom )
                        sheet.write(row , col+8, ' ',bottom )
                        sheet.write(row , col+9, '',bottom )
                        row += 1
                        i=0
                        for line in cession.plus_values_fusion_line_ids:
                            i+=1
                            sheet.write(row, col, i , border_left_right_name )
                            sheet.write(row, col+1, line.name,border_left_right_vals )
                            sheet.write(row, col+2, line.valeur_apport,border_left_right_vals )
                            sheet.write(row, col+3, line.valeur_nette_comptable,border_left_right_vals )
                            sheet.write(row, col+4, line.plus_value_constatee,border_left_right_vals )
                            sheet.write(row, col+5, line.fraction_exercice_ant,border_left_right_vals )
                            sheet.write(row, col+6, line.fraction_exercice_actuel,border_left_right_vals )
                            sheet.write(row, col+7, line.cumul_plus_value_rapportee,border_left_right_vals )
                            sheet.write(row, col+8, line.solde_plus_value_non_rapportee,border_left_right_vals )
                            sheet.write(row, col+9, line.observations,border_left_right_vals )
                            row += 1
                    if model.model == 'interets.emprunts':
                        sheet = workbook.add_worksheet('Interets')
                        cession = self.env['interets.emprunts'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°18')
                        sheet.write(0, 15, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:P3', 'ETAT DES INTERETS DES EMPRUNTS CONTRACTES AUPRES DES ASSOCIES ET DES TIERS', title)
                        sheet.merge_range('A4:P4', 'AUTRES QUE LES ORGANISMES DE BANQUE OU DE CREDIT', title)
                        row = 6
                        col = 0
                        # Header row
                        sheet.write(row , col, '',border_top_header )
                        sheet.write(row , col+1, '', border_top_header)
                        sheet.write(row , col+2, ' ',border_top_header )
                        sheet.write(row , col+3, ' ',border_top_header )
                        sheet.write(row , col+4, '',border_top_header )
                        sheet.write(row , col+5, '',border_top_header )
                        sheet.write(row , col+6, '',top_left )
                        sheet.write(row , col+7, '',top_top )
                        sheet.write(row , col+8, 'PRÊT',top_top )
                        sheet.write(row , col+9, '',top_top )
                        sheet.write(row , col+10, '',top_right )
                        sheet.write(row , col+11, 'REMB. EX. ',top_left )
                        sheet.write(row , col+12, 'ANTERIEURS',top_right )
                        sheet.write(row , col+13, 'REMB. EX',top_left )
                        sheet.write(row , col+14, 'ACTUEL',top_right )
                        sheet.write(row , col+15, '', )
                        row += 1
                        sheet.write(row , col, 'CAT.',border_left_right_header )
                        sheet.write(row , col+1, 'NOM ET PRENOM', border_left_right_header)
                        sheet.write(row , col+2, 'RAISON SOCIAL',border_left_right_header )
                        sheet.write(row , col+3, 'ADRESSE',border_left_right_header )
                        sheet.write(row , col+4, 'I.F',border_left_right_header )
                        sheet.write(row , col+5, 'N° CIN',border_left_right_header )
                        sheet.write(row , col+6, 'MONTANT',border_top_header )
                        sheet.write(row , col+7, 'DATE',border_top_header )
                        sheet.write(row , col+8, 'DUREE',border_top_header )
                        sheet.write(row , col+9, 'TAUX',border_top_header )
                        sheet.write(row , col+10, 'CHARGE',border_top_header )
                        sheet.write(row , col+11, 'PRINCIPAL',border_top_header )
                        sheet.write(row , col+12, 'INTERETS',border_top_header )
                        sheet.write(row , col+13 ,'PRINCIPAL',border_top_header )
                        sheet.write(row , col+14, 'INTERETS',border_top_header )
                        sheet.write(row , col+15, 'OBSERVATION',border_top_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, ' ', border_left_right_header)
                        sheet.write(row , col+2, ' ',border_left_right_header )
                        sheet.write(row , col+3, ' ',border_left_right_header )
                        sheet.write(row , col+4, ' ',border_left_right_header )
                        sheet.write(row , col+5, '  ',border_left_right_header )
                        sheet.write(row , col+6, '   ',border_left_right_header )
                        sheet.write(row , col+7, ' ',border_left_right_header )
                        sheet.write(row , col+8, 'EN MOIS',border_left_right_header )
                        sheet.write(row , col+9, 'INTERET',border_left_right_header )
                        sheet.write(row , col+10, 'FINANCIERE',border_left_right_header )
                        sheet.write(row , col+11, ' ',border_left_right_header )
                        sheet.write(row , col+12, ' ',border_left_right_header )
                        sheet.write(row , col+13, ' ',border_left_right_header )
                        sheet.write(row , col+14, ' ',border_left_right_header )
                        sheet.write(row , col+15, ' ',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',bottom )
                        sheet.write(row , col+1, '', bottom)
                        sheet.write(row , col+2, ' ',bottom )
                        sheet.write(row , col+3, '',bottom )
                        sheet.write(row , col+4, ' ',bottom )
                        sheet.write(row , col+5, '',bottom )
                        sheet.write(row , col+6, '',bottom )
                        sheet.write(row , col+7, '',bottom )
                        sheet.write(row , col+8, '',bottom )
                        sheet.write(row , col+9, '',bottom )
                        sheet.write(row , col+10, 'GLOBALE',bottom )
                        sheet.write(row , col+11, '',bottom )
                        sheet.write(row , col+12, '',bottom )
                        sheet.write(row , col+13, '',bottom )
                        sheet.write(row , col+14, '',bottom )
                        sheet.write(row , col+15, '',bottom )
                        row += 1
                        i=0
                        for line in cession.interets_emprunts_line_ids:
                            i+=1
                            sheet.write(row, col, line.name ,border_left_right_name )
                            sheet.write(row, col+1, line.code,border_left_right_vals )
                            sheet.write(row, col+2, line.adresse,border_left_right_vals )
                            sheet.write(row, col+3, line.n_if,border_left_right_vals )
                            sheet.write(row, col+4, line.cin,border_left_right_vals )
                            sheet.write(row, col+5, line.montant_pret,border_left_right_vals )
                            sheet.write(row, col+6, line.date_pret,border_left_right_vals )
                            sheet.write(row, col+7, line.duree_pret,border_left_right_vals )
                            sheet.write(row, col+8, line.taux_interet,border_left_right_vals )
                            sheet.write(row, col+9, line.charge_financiere,border_left_right_vals )
                            sheet.write(row, col+10, line.remboursement_exercice_ant_principal,border_left_right_vals )
                            sheet.write(row, col+11, line.remboursement_exercice_ant_intertet,border_left_right_vals )
                            sheet.write(row, col+12, line.remboursement_exercice_actuel_principal,border_left_right_vals )
                            sheet.write(row, col+13, line.remboursement_exercice_actuel_intertet,border_left_right_vals )
                            sheet.write(row, col+14, line.remboursement_exercice_ant,border_left_right_vals )
                            sheet.write(row, col+15, line.observations,border_left_right_vals )
                            row += 1
                        if not cession.interets_emprunts_line_ids:
                            for i  in range(20):
                                i+=1
                                sheet.write(row, col, '',bottom )
                                sheet.write(row, col+1, '',bottom )
                                sheet.write(row, col+2, '',bottom )
                                sheet.write(row, col+3, '',bottom )
                                sheet.write(row, col+4, '',bottom )
                                sheet.write(row, col+5,'',bottom )
                                sheet.write(row, col+6, '',bottom )
                                sheet.write(row, col+7,'',bottom )
                                sheet.write(row, col+8,'',bottom )
                                sheet.write(row, col+9, '',bottom )
                                sheet.write(row, col+10,'',bottom )
                                sheet.write(row, col+11,'',bottom )
                                sheet.write(row, col+12, '',bottom )
                                sheet.write(row, col+13, '',bottom )
                                sheet.write(row, col+14, '',bottom )
                                sheet.write(row, col+15, '',bottom )
                                row += 1
                    if model.model == 'locations.baux':
                        sheet = workbook.add_worksheet('location')
                        cession = self.env['locations.baux'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°19')
                        sheet.write(0, 13, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:M3', 'TABLEAU DES LOCATIONS ET BAUX AUTRES QUE LE CREDIT-BAIL', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.write(row , col, '',border_top_header )
                        sheet.write(row , col+1, '', border_top_header)
                        sheet.write(row , col+2, ' ',border_top_header )
                        sheet.write(row , col+3, ' ',border_top_header )
                        sheet.write(row , col+4, '',border_top_header )
                        sheet.write(row , col+5, '',border_top_header )
                        sheet.write(row , col+6, '',border_top_header )
                        sheet.write(row , col+7, '',border_top_header )
                        sheet.write(row , col+8, 'DATE DE ',border_top_header )
                        sheet.write(row , col+9, 'MONTANT',border_top_header )
                        sheet.write(row , col+10, 'MONTANT LOYER',border_top_header )
                        sheet.write(row , col+11, 'NATURE',top_left )
                        sheet.write(row , col+12, 'CONTRAT (1)', top_right)
                        row += 1
                        sheet.write(row , col, 'NATURE',border_left_right_header )
                        sheet.write(row , col+1, 'LIEU DE', border_left_right_header)
                        sheet.write(row , col+2, 'NOM ET PRENOM',border_left_right_header )
                        sheet.write(row , col+3, 'RAISON SOCIAL',border_left_right_header )
                        sheet.write(row , col+4, 'ADRESSE',border_left_right_header )
                        sheet.write(row , col+5, 'N° IF',border_left_right_header )
                        sheet.write(row , col+6, 'N° CNI',border_left_right_header )
                        sheet.write(row , col+7, 'N° C.E',border_left_right_header )
                        sheet.write(row , col+8, 'CONCLUSION',border_left_right_header )
                        sheet.write(row , col+9, 'ANNUEL',border_left_right_header )
                        sheet.write(row , col+10, 'COMPRIS',border_left_right_header )
                        sheet.write(row , col+11, 'BAIL',border_left_right_header )
                        sheet.write(row , col+12, 'LEASING',border_top_header )
                        row += 1
                        sheet.write(row , col, 'DU BIEN LOUE',border_left_right_header )
                        sheet.write(row , col+1, 'SITUATION', border_left_right_header)
                        sheet.write(row , col+2, 'DU PROPRIETAIRE',border_left_right_header )
                        sheet.write(row , col+3, 'DU PROPRIETAIRE',border_left_right_header )
                        sheet.write(row , col+4, 'DU PROPRIETAIRE',border_left_right_header )
                        sheet.write(row , col+5, 'DU',border_left_right_header )
                        sheet.write(row , col+6, 'DU',border_left_right_header )
                        sheet.write(row , col+7, 'DU',border_left_right_header )
                        sheet.write(row , col+8, 'DE L\'ACTE',border_left_right_header )
                        sheet.write(row , col+9, 'DE LOCATION',border_left_right_header )
                        sheet.write(row , col+10, 'DANS',border_left_right_header )
                        sheet.write(row , col+11, 'ORDINAIRE',border_left_right_header )
                        sheet.write(row , col+12, '(Nème',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, '', border_left_right_header)
                        sheet.write(row , col+2, ' ',border_left_right_header )
                        sheet.write(row , col+3, '',border_left_right_header )
                        sheet.write(row , col+4, ' ',border_left_right_header )
                        sheet.write(row , col+5, 'PROPRIETAIRE',border_left_right_header )
                        sheet.write(row , col+6, 'PROPRIETAIRE',border_left_right_header )
                        sheet.write(row , col+7, 'PROPRIETAIRE',border_left_right_header )
                        sheet.write(row , col+8, ' DE LOCATION',border_left_right_header )
                        sheet.write(row , col+9, '',border_left_right_header )
                        sheet.write(row , col+10, ' LES CHARGES',border_left_right_header )
                        sheet.write(row , col+11, '',border_left_right_header )
                        sheet.write(row , col+12, 'période)',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, '', border_left_right_header)
                        sheet.write(row , col+2, ' ',border_left_right_header )
                        sheet.write(row , col+3, '',border_left_right_header )
                        sheet.write(row , col+4, ' ',border_left_right_header )
                        sheet.write(row , col+5, '',border_left_right_header )
                        sheet.write(row , col+6, '',border_left_right_header )
                        sheet.write(row , col+7, '',border_left_right_header )
                        sheet.write(row , col+8, 'ET DIFFEREE',border_left_right_header )
                        sheet.write(row , col+9, '',border_left_right_header )
                        sheet.write(row , col+10, 'DE L\'EXERCICE',border_left_right_header )
                        sheet.write(row , col+11, '',border_left_right_header )
                        sheet.write(row , col+12, '',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '1',bottom )
                        sheet.write(row , col+1, '2', bottom)
                        sheet.write(row , col+2, '3',bottom )
                        sheet.write(row , col+3, '4',bottom )
                        sheet.write(row , col+4, '5',bottom )
                        sheet.write(row , col+5, '6',bottom )
                        sheet.write(row , col+6, '7',bottom )
                        sheet.write(row , col+7, '8',bottom )
                        sheet.write(row , col+8, '9',bottom )
                        sheet.write(row , col+9, '10',bottom )
                        sheet.write(row , col+10, '11',bottom )
                        sheet.write(row , col+11, '12',bottom )
                        sheet.write(row , col+12, '13',bottom )
                        row += 1
                        i=0
                        for line in cession.locations_baux_line_ids:
                            i+=1
                            sheet.write(row, col, line.name ,border_left_right_name )
                            sheet.write(row, col+1, line.lieu_situation,border_left_right_vals )
                            sheet.write(row, col+2, line.nom_prenom,border_left_right_vals )
                            sheet.write(row, col+3, line.raison,border_left_right_vals )
                            sheet.write(row, col+4, line.adress,border_left_right_vals )
                            sheet.write(row, col+5, line.n_if,border_left_right_vals )
                            sheet.write(row, col+6, line.n_cni,border_left_right_vals )
                            sheet.write(row, col+7, line.card_num,border_left_right_vals )
                            sheet.write(row, col+8, line.date_conclusion,border_left_right_vals )
                            sheet.write(row, col+9, line.montant_annuel,border_left_right_vals )
                            sheet.write(row, col+10, line.montant_loyer,border_left_right_vals )
                            sheet.write(row, col+11, line.nature_contrat_bail,border_left_right_vals )
                            sheet.write(row, col+12, line.nature_contrat_period,border_left_right_vals )
                            row += 1
                        
                        if not cession.locations_baux_line_ids:
                            for i  in range(20):
                                i+=1
                                sheet.write(row, col, '',bottom )
                                sheet.write(row, col+1, '',bottom )
                                sheet.write(row, col+2, '',bottom )
                                sheet.write(row, col+3, '',bottom )
                                sheet.write(row, col+4, '',bottom )
                                sheet.write(row, col+5,'',bottom )
                                sheet.write(row, col+6, '',bottom )
                                sheet.write(row, col+7,'',bottom )
                                sheet.write(row, col+8,'',bottom )
                                sheet.write(row, col+9, '',bottom )
                                sheet.write(row, col+10,'',bottom )
                                sheet.write(row, col+11,'',bottom )
                                sheet.write(row, col+12, '',bottom )
                                row += 1
                            
                    if model.model == 'detail.stock':
                        sheet = workbook.add_worksheet('Stock')
                        cession = self.env['detail.stock'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(1, 0, 'Tableau N°20')
                        sheet.write(0, 7, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:H3', 'ETAT DETAILLE DES STOCKS', title)
                        row = 5
                        col = 0
                        # Header row
                        sheet.write(row , col, '',border_top_header )
                        sheet.write(row , col+1, '', top_left)
                        sheet.write(row , col+2, 'STOCK FINAL',top_top )
                        sheet.write(row , col+3, ' ',top_right )
                        sheet.write(row , col+4, '',top_left )
                        sheet.write(row , col+5, 'STOCK INITIAL',top_top )
                        sheet.write(row , col+6, '',top_right )
                        sheet.write(row , col+7, 'VARIATION DE',border_top_header )
                        row += 1
                        sheet.write(row , col, 'STOCKS',border_left_right_header )
                        sheet.write(row , col+1, 'MONTANT', top_left)
                        sheet.write(row , col+2, 'PROVISION',top_top )
                        sheet.write(row , col+3, 'MONTANT',top_right )
                        sheet.write(row , col+4, 'MONTANT',top_left )
                        sheet.write(row , col+5, 'PROVISION',top_top )
                        sheet.write(row , col+6, 'MONTANT',top_right )
                        sheet.write(row , col+7, 'STOCK EN VALEUR',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, 'BRUT', border_left_right_header)
                        sheet.write(row , col+2, 'POUR',border_left_right_header )
                        sheet.write(row , col+3, 'NET',border_left_right_header )
                        sheet.write(row , col+4, 'BRUT',border_left_right_header )
                        sheet.write(row , col+5, 'POUR',border_left_right_header )
                        sheet.write(row , col+6, 'NET',border_left_right_header )
                        sheet.write(row , col+7, '(+ ou -)',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',border_left_right_header )
                        sheet.write(row , col+1, '', border_left_right_header)
                        sheet.write(row , col+2, 'DEPRECIATION',border_left_right_header )
                        sheet.write(row , col+3, '',border_left_right_header )
                        sheet.write(row , col+4, ' ',border_left_right_header )
                        sheet.write(row , col+5, 'DEPRECIATION',border_left_right_header )
                        sheet.write(row , col+6, '',border_left_right_header )
                        sheet.write(row , col+7, '7 = 6 - 3',border_left_right_header )
                        row += 1
                        sheet.write(row , col, '',bottom )
                        sheet.write(row , col+1, '', bottom)
                        sheet.write(row , col+2, ' ',bottom )
                        sheet.write(row , col+3, '',bottom )
                        sheet.write(row , col+4, ' ',bottom )
                        sheet.write(row , col+5, '',bottom )
                        sheet.write(row , col+6, '',bottom )
                        sheet.write(row , col+7, '',bottom )
                        row += 1
                        for line in cession.detail_stock_line_ids:
                            sheet.write(row, col, line.name ,border_left_right_name )
                            sheet.write(row, col+1, line.montant_brut_stock_final,border_left_right_vals )
                            sheet.write(row, col+2, line.provisions_stock_final,border_left_right_vals )
                            sheet.write(row, col+3, line.montant_net_stock_final,border_left_right_vals )
                            sheet.write(row, col+4, line.montant_brut_stock_initial,border_left_right_vals )
                            sheet.write(row, col+5, line.provisions_stock_initial,border_left_right_vals )
                            sheet.write(row, col+6, line.montant_net_stock_initial,border_left_right_vals )
                            sheet.write(row, col+7, line.variation_stock,border_left_right_vals )
                            row += 1
                    if model.model == 'finance.first':
                        string = ''
                        sheet = workbook.add_worksheet('Financement')
                        financement_1 = self.env['finance.first'].search(domain)
                        financement_2 = self.env['finance.second'].search(domain)
                        sheet.write(0, 0, 'Raison sociale : ' + str(company.name))
                        sheet.write(0, 2, 'Exercice : ' + str(date_range.date_start) + '-' + str(date_range.date_end))
                        sheet.merge_range('A3:E3', 'TABLEAU DE FINANCEMENT DE L\'EXERCICE', title) 
                        sheet.merge_range('A5:E5','I- SYNTHESE DES MASSES DU BILAN',bold)
                        row = 6
                        col = 0
                        # Header row
                        sheet.write(row , col, '',border_top_header )
                        sheet.write(row , col+1, 'EXERCICE',border_top_header )
                        sheet.write(row , col+2, 'EXERCICE PRECEDENT',border_top_header )
                        sheet.write(row , col+3, ' VARIATION',top_left )
                        sheet.write(row , col+4, ' (A-B)',top_right )
                        row += 1
                        sheet.write(row , col, 'MASSES',border_left_right_header )
                        sheet.write(row , col+1, '',border_left_right_header )
                        sheet.write(row , col+2, '',border_left_right_header )
                        sheet.write(row , col+3, ' EMPLOIS',top_left )
                        sheet.write(row , col+4, 'RESSOURCES',top_right )
                        row += 1
                        sheet.write(row , col, '',bottom )
                        sheet.write(row , col+1, 'a',bottom )
                        sheet.write(row , col+2, 'b',bottom )
                        sheet.write(row , col+3, 'c',bottom )
                        sheet.write(row , col+4, 'd',bottom )
                        row += 1
                        for line in financement_1.line_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, line.montant_debut,border_left_right_vals)
                            sheet.write(row, col+2, line.montant_fin,border_left_right_vals)
                            sheet.write(row, col+3, line.p_debit_fin,border_left_right_vals)
                            sheet.write(row, col+4, line.n_debit_fin,border_left_right_vals)
                            row += 1
                        row += 1
                        # Header row
                        string = 'A'+str(row)+':'+'E'+str(row)
                        sheet.merge_range(string,'II- EMPLOIS ET RESSOURCES',bold)
                        sheet.write(row , col, 'NATURE',border_top_header )
                        sheet.write(row , col+1, 'EXERCICE',top_left )
                        sheet.write(row , col+2, '',top_right )
                        sheet.write(row , col+3, ' EXERCICE ',top_left )
                        sheet.write(row , col+4, ' PRECEDENT',top_right )
                        row += 1
                        sheet.write(row , col, '',bottom )
                        sheet.write(row , col+1, 'EMPLOIS',bottom )
                        sheet.write(row , col+2, 'RESSOURCES',bottom )
                        sheet.write(row , col+3, 'EMPLOIS',bottom )
                        sheet.write(row , col+4, 'RESSOURCES',bottom )
                        row += 1
                        for line in financement_2.line_ids:
                            sheet.write(row, col, line.name,border_left_right_name)
                            sheet.write(row, col+1, line.emploi_debut,border_left_right_vals)
                            sheet.write(row, col+2, line.ressource_debut,border_left_right_vals)
                            sheet.write(row, col+3, line.emploi_fin,border_left_right_vals)
                            sheet.write(row, col+4, line.ressource_fin,border_left_right_vals)
                            row += 1
                    
                    