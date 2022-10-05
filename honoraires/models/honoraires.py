# -*- coding: utf-8 -*-

from odoo import models, fields, api
import os

directory = os.path.dirname(__file__)

from lxml import etree
import base64
import zipfile
try:
    from openpyxl import load_workbook
except ImportError:
    pass
import io


class Honoraire(models.Model):
    _name = "honoraire"
    _description = "Honoraire"
    _inherit = ['mail.thread']

    name = fields.Char(string=u'Description', required=True, default=u"Déclaration des honoraires")
    date = fields.Date(string=u'Date', required=True)
    fiscal_year_id = fields.Many2one('date.range',
                               string=u'Exercice fiscal', domain=[('type_id.fiscal_year','=',True)], required=True)
    company_id = fields.Many2one('res.company', string=u'Societé', default=lambda self: self.env.user.company_id)
    line_ids = fields.One2many(comodel_name='honoraire.line', inverse_name='honoraire_id',
                                  string=u'Terrains')

    honoraire_rapport_excel = fields.Binary(string="Rapport Honoraires Excel")
    xml_file = fields.Binary('Rapport Honoraires XML', attachment=True)

    state = fields.Selection([
        ('draft', u'Brouillon'),
        ('done', u'Valide')], default='draft', string='Etat', readonly=True, track_visibility='onchange')

    # @api.multi
    def generate_data(self):
        account_invoice_obj = self.env['account.move']
        honoraire_line_obj = self.env['honoraire.line']
        for record in self:
            record.line_ids.unlink()
            invoice_domain = [('date', '>=', self.fiscal_year_id.date_start),
                              ('date', '<=', self.fiscal_year_id.date_end),
                              ('partner_id.honoraire', '=', True),
                              ('move_type', '=', 'in_invoice'),
                              ('state', '=', 'posted')]
            invoice_ids = account_invoice_obj.read_group(invoice_domain,fields=['partner_id', 'amount_untaxed'], groupby=['partner_id'])
            invoices_by_partner = dict((item['partner_id'][0], item['amount_untaxed']) for item in invoice_ids)
            for key, value in invoices_by_partner.items():
                vals = {
                        'partner_id': key,
                        'montant_honoraires': value,
                        'honoraire_id': record.id,
                        }
                honoraire_line_obj.create(vals)

            avoir_domain = [('date', '>=', self.fiscal_year_id.date_start),
                            ('date', '<=', self.fiscal_year_id.date_end),
                            ('partner_id.honoraire', '=', True),
                            ('move_type', '=', 'in_refund'),
                            ('state', '=', 'posted')]
            avoir_ids = account_invoice_obj.read_group(avoir_domain,fields=['partner_id', 'amount_total'], groupby=['partner_id'])
            avoirs_by_partner = dict((item['partner_id'][0], item['amount_total']) for item in avoir_ids)
            for key, value in avoirs_by_partner.items():
                honoraire_line_id = honoraire_line_obj.search([['partner_id','=',key],
                                                               ['honoraire_id', '=', record.id],
                                                               ])
                if honoraire_line_id:
                    honoraire_line_id.write({'montant_avoirs':value})
                else:
                    vals = {
                            'partner_id':key,
                            'montant_avoirs':value,
                            'honoraire_id':record.id,
                            }
                    honoraire_line_obj.create(vals)

    # @api.multi
    def genetare_tp_file(self):
        report_template = self.env['ir.config_parameter'].sudo().get_param('honoraires.honoraire_rapport_excel')
        for record in self:
            file = base64.b64decode(report_template)
            xls_filelike = io.BytesIO(file)
            wb = load_workbook(xls_filelike)
            sheet1 = wb.worksheets[0]
            sheet2 = wb.worksheets[1]
            sheet3 = wb.worksheets[2]
            # TABLE 0 INFOS
            sheet1['K13'] = record.fiscal_year_id.date_start
            sheet1['U13'] = record.fiscal_year_id.date_end
            sheet1['K17'] = record.company_id.partner_id.name
            sheet1['K19'] = record.company_id.partner_id.id_fisc
            sheet1['P21'] = record.company_id.partner_id.itp
            sheet1['A24'] = record.company_id.partner_id.street
            sheet1['Y24'] = record.company_id.partner_id.city
            sheet1['K26'] = record.company_id.partner_id.activites
            # TABLE 1
            j = 11
            total_honoraires = 0.0
            total_avoirs = 0.0
            for line in record.line_ids:
                sheet2['B' + str(j)] = "Nom et prénom ou raison sociale:"+ str(line.partner_id.name.encode('utf8'))
                sheet2['B' + str(j+1)] = "N° d'identification fiscale:" + str(line.partner_id.id_fisc)
                sheet2['B' + str(j+2)] = "N° affiliation CNSS" + str(line.partner_id.cnss)
                sheet2['B' + str(j+3)] = "N° d'identification à la  TP : " + str(line.partner_id.itp)
                sheet2['B' + str(j+4)] = "Adresse du siège social ou du principal établissement ou du domicile fiscal:"
                if line.partner_id.street:
                    sheet2['B' + str(j+5)] = "" +str(line.partner_id.street.encode('utf8'))
                else:
                    sheet2['B' + str(j + 5)] = ""
                if line.partner_id.city:
                    sheet2['B' + str(j+6)] = "Ville :" + str(line.partner_id.city.encode('utf8'))
                else:
                    sheet2['B' + str(j + 6)] = "Ville :"
                if line.partner_id.activites:
                    sheet2['B' + str(j+7)] = "Profession ou activité (4) :" + str(line.partner_id.activites.encode('utf8'))
                else:
                    sheet2['B' + str(j + 7)] = "Profession ou activité (4) :"
                if line.partner_id.nationalite:
                    sheet2['B' + str(j+8)] = "Nationalité : " + str(line.partner_id.nationalite.encode('utf8'))
                else:
                    sheet2['B' + str(j + 8)] = "Nationalité : "

                sheet2['AE' + str(j)] = line.montant_honoraires
                sheet2['AP' + str(j)] = line.montant_avoirs
                j+=10
                total_honoraires += line.montant_honoraires
                total_avoirs += line.montant_avoirs

            sheet2['AE' + str(j+1)] = total_honoraires
            sheet2['AP' + str(j+1)] = total_avoirs

            # TABLE 2
            sheet3['G21'] = record.fiscal_year_id.date_start
            sheet3['Q21'] = record.fiscal_year_id.date_end
            sheet3['L26'] = record.company_id.partner_id.id_fisc
            sheet3['L28'] = record.company_id.partner_id.name
            # wb = base64.encodestring(wb)
            # base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            # attachment_obj = self.env['ir.attachment']
            # # create attachment
            # attachment_id = attachment_obj.create(
            #     {'name': "simple_is",'store_fname':"honoraire.xlsx'","mimetype":"text/xlsx", 'datas': wb})
            # # prepare download url
            # download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
            # # download
            # return {
            #     "type": "ir.actions.act_url",
            #     "url": str(base_url) + str(download_url),
            #     "target": "new"}
            wb.save(os.path.join(directory,"honoraire.xlsx"))
            honoraire_rapport_excel = base64.encodestring(open(os.path.join(directory,'honoraire.xlsx'), 'rb').read())
            record.write({'honoraire_rapport_excel': honoraire_rapport_excel})
        return True

    # @api.multi
    def generate_xml_file(self):
        for record in self:
            root = etree.Element("DeclarationRVT")
            etree.SubElement(root,"identifiantFiscal").text = str(record.company_id.partner_id.id_fisc)
            etree.SubElement(root,"exerciceFiscalDu").text = str((record.fiscal_year_id.date_start).strftime('%Y-%m-%d'))
            etree.SubElement(root,"exerciceFiscalAu").text = str((record.fiscal_year_id.date_end).strftime('%Y-%m-%d'))
            sommesAllouees = etree.SubElement(root,"sommesAllouees")
            for line in record.line_ids:
                SommeAllouee = etree.SubElement(sommesAllouees,"SommeAllouee")
                etree.SubElement(SommeAllouee, "honoraires").text = str(line.montant_honoraires)
                etree.SubElement(SommeAllouee, "commissions").text = str(line.montant_avoirs)
                etree.SubElement(SommeAllouee, "rabais").text = str(line.montant_retenue)
                beneficiaire = etree.SubElement(SommeAllouee, "beneficiaire")
                etree.SubElement(beneficiaire, "identifiantFiscal").text = str(line.partner_id.id_fisc)
                etree.SubElement(beneficiaire, "raisonSociale").text = str(line.partner_id.name.encode('utf8'))
                etree.SubElement(beneficiaire, "adresse").text = str(line.partner_id.street) and str(line.partner_id.street.encode('utf8')) if (line.partner_id.street) else ''
                etree.SubElement(beneficiaire, "numeroTP").text = str(line.partner_id.itp)
                etree.SubElement(beneficiaire, "numCNSS").text = str(line.partner_id.cnss)
                etree.SubElement(beneficiaire, "ville").text = str(line.partner_id.city) and str(line.partner_id.city.encode('utf8')) if (line.partner_id.city) else ''
                etree.SubElement(beneficiaire, "profession").text = str(line.partner_id.activites) and str(line.partner_id.activites.encode('utf8')) if (line.partner_id.activites) else ''
                etree.SubElement(beneficiaire, "nationalite").text = str(line.partner_id.nationalite) and str(line.partner_id.nationalite.encode('utf8')) if (line.partner_id.nationalite) else ''

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

class HonoraireLine(models.Model):
    _name = "honoraire.line"
    _description = "Ligne honoraire"

    partner_id = fields.Many2one(comodel_name="res.partner", string=u"Bénéficiaire", required=False, )
    montant_honoraires = fields.Float(string=u"Montant des honoraires",  required=False, )
    montant_avoirs = fields.Float(string=u"RRR",  required=False, )
    montant_retenue = fields.Float(string=u"Montant de la retenue",  required=False, )
    honoraire_id = fields.Many2one(comodel_name="honoraire", string="Honoraire", required=False, )