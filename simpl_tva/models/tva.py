# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from lxml import etree
import base64
import zipfile


import os
directory = os.path.dirname(__file__)


class TvaDeclaration(models.Model):
    _inherit = "tva.declaration"

    xml_file = fields.Binary(u'Fichier XML', attachment=True)
    name_file = fields.Char(string=u"Nom fichier", required=False, )

    def generate_xml_file(self):
        for record in self:
            if not record.company_id.partner_id.id_fisc:
                raise ValidationError(u"Vous devez impérativement renseigner l'IF de la société!")
            root = etree.Element("DeclarationReleveDeduction")
            etree.SubElement(root, "identifiantFiscal").text = str(record.company_id.partner_id.id_fisc)
            etree.SubElement(root, "annee").text = str(record.annee)
            etree.SubElement(root, "periode").text = str(record.period)
            etree.SubElement(root, "regime").text = str(record.regime)
            releveDeductions = etree.SubElement(root, "releveDeductions")
            for line in record.line_ids:
                rd = etree.SubElement(releveDeductions, "rd")
                etree.SubElement(rd, "ord").text = str(line.sequence)
                etree.SubElement(rd, "num").text = str(line.invoice_number)
                etree.SubElement(rd, "des").text = str(line.description)
                etree.SubElement(rd, "mht").text = str(line.amount_ht)
                etree.SubElement(rd, "tva").text = str(line.amount_tva)
                etree.SubElement(rd, "ttc").text = str(line.amount_ttc)
                # TO DO ajouter le prorata
                fr = etree.SubElement(rd, "refF")
                etree.SubElement(fr, "if").text = str(line.id_fisc)
                etree.SubElement(fr, "nom").text = str(line.partner_name)
                etree.SubElement(fr, "ice").text = str(line.ice)
                etree.SubElement(rd, "tx").text = str(round(line.tax_rate, 2))
                etree.SubElement(rd, "prorata").text = str(int(line.tax_id.prorata))
                mp = etree.SubElement(rd, "mp")
                etree.SubElement(mp, "id").text = str(line.paiement_type.code)
                etree.SubElement(rd, "dpai").text = str(line.paiement_date)
                etree.SubElement(rd, "dfac").text = str(line.invoice_date)
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
