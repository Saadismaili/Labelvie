# -*- encoding: utf-8 -*-

from odoo import models,fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    id_fisc = fields.Char(string=u'Identifiant Fiscal')
    rc = fields.Char(string=u'RC')
    cnss = fields.Char(string=u'Numéro de la sécurité sociale')
    capital_social = fields.Char(string=u'Capital social')
    ice = fields.Char(string=u'ICE')
    itp = fields.Char(string=u'Identifiant Taxe Professionnelle')
    activites = fields.Char(string=u"Profession ou activités exercées")
    nationalite = fields.Char(string=u"Nationalité")
    fax = fields.Char(string=u"Fax")


    # @api.one
    @api.constrains('ice')
    def _check_ice(self):
        if self.ice and (len(self.ice) != 15 or not self.ice.isdigit()):
                raise ValidationError(u"L'ICE doit être constitué de 15 chiffres")


class PartnerXlsx(models.AbstractModel):
    _name = 'report.partner_extend.partner_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, obj.name, bold)