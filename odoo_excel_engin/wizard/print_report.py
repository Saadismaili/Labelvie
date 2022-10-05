# -*- coding: utf-8 -*-

from odoo import models, api,fields , _
from odoo.exceptions import UserError


class PrintReport(models.TransientModel):

    _name = "report.engin.print"
    _description = "Report engin print"

    report_id = fields.Many2one('report.group', 'Type de liasse')
    selection = fields.Boolean(u'Sélection des tableaux')
    report_ids = fields.Many2many('report.engin', 'engin_report_rel', 'engin_report_id', 'report_id', 'Rapports')
    fy_n_id = fields.Many2one('date.range', 'Exercice fiscal')
    xml_file = fields.Binary(u'Fichier de Télé-Déclaration IS')
    name = fields.Char('Nom du fichier', readonly=True)
    # company_id = fields.Many2one('res.company', u'Société', default=lambda self: self.env.user.company_id, required=False)

    # @api.multi
    def print_report(self):
        self.ensure_one()
        ex_n = self.fy_n_id.id
        if not self.fy_n_id.previous_fiscal_year:
            raise UserError(_(
                u"Merci de préciser l'exercice précédant de l'exercice choisi!"))
        ex_n_1 = self.fy_n_id.previous_fiscal_year.id
        report_list = []
        for record in self:
            if record.report_id and not record.selection:
                for report in record.report_id.rapport_ids:
                    report_list.append(report.report_id.id)
            if record.report_ids and record.selection:
                for report in record.report_ids:
                    report_list.append(report.id)
        return self.env['report'].with_context(ex_n=ex_n,ex_n_1=ex_n_1).get_action(self.env['report.engin'].browse(report_list), 'report.engin.xlsx')
