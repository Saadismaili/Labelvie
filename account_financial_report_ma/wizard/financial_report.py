# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, api, fields , _
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.exceptions import ValidationError

class FinancialReport(models.TransientModel):
    """
    The class print report to add GL and Balance reports.
    """
    _name = "financial.report"
    _description = "Rapports Financiers"


    partenaire_detail = fields.Boolean('Détail des partenaires')
    date_range_exercice_id = fields.Many2one(
        comodel_name='date.range',
        string='Exercice fiscal',
        required = True
    )
    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string=u'Période fiscale'
    )
    date_from = fields.Date('Date de', required=True)
    date_to = fields.Date('Date au', required=True)
    target_move = fields.Selection([('posted', 'Comptabilise'),
                                    ('all', 'Tous')],
                                   string=u'Écritures ciblées',
                                   required=True,
                                   default='all')
    target_accounts = fields.Selection([('partners', 'Partenaires'),
                                        ('accounts', 'Comptes')],
                                       string=u'Comptes ciblés',
                                       required=True,
                                       default='accounts')
    target_report = fields.Selection([('gl', 'Grand livre'),
                                        ('balance', 'Balance')],
                                       string=u'Rapport ciblé',
                                       required=True,
                                       default='gl')

    company_id = fields.Many2one('res.company', string='Société', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Filtrer comptes',
    )
    customers = fields.Boolean('Client')
    suppliers = fields.Boolean('Fournisseur')

    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Filter partners',
    )
    code_from = fields.Char(
        string=u'Code de',
    )
    code_to = fields.Char(
        string=u'Code à',
    )

    @api.onchange('date_range_exercice_id')
    def onchange_date_range_exercice_id(self):
        self.date_from = self.date_range_exercice_id.date_start
        self.date_to = self.date_range_exercice_id.date_end

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        """Handle date range change."""
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.onchange('code_from', 'code_to')
    def onchange_account_ids(self):
        """Handle account change."""
        domain = []
        if self.code_from and self.code_to:
            domain += [('code', '>=', self.code_from), ('code', '<=', self.code_to), ('deprecated', '=', False)]
            self.account_ids = self.env['account.account'].search(domain)

    # @api.multi
    def onchange_date_search(self):
        """ Make sure the date range is correct"""
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValidationError(
                    u"La plage de date n'est pas correcte !")


    @api.onchange('receivable_accounts_only', 'payable_accounts_only')
    def onchange_type_accounts_only(self):
        """Handle receivable/payable accounts only change."""
        lst_account = []
        cr = self.env.cr
        if self.receivable_accounts_only or self.payable_accounts_only:
            if self.receivable_accounts_only and self.payable_accounts_only:
               cr.execute(
                   "SELECT distinct id FROM account_account as a "
                   " where a.internal_type in ('receivable', 'payable')"
                   "and a.company_id = %s", (self.company_id.id,))
            elif self.receivable_accounts_only:
                cr.execute(
                    "SELECT distinct id FROM account_account as a "
                    " where a.internal_type = 'receivable'"
                    "and a.company_id = %s", (self.company_id.id,))
            elif self.payable_accounts_only:
                cr.execute(
                    "SELECT distinct id FROM account_account as a "
                    " where a.internal_type = 'payable'"
                    "and a.company_id = %s", (self.company_id.id,))
            account_ids = cr.fetchall()
            for account in account_ids:
                lst_account.append(account[0])
            self.account_ids = self.env['account.account'].browse(lst_account)
        else:
            self.account_ids = None

    # @api.onchange('customers', 'suppliers')
    def onchange_partners(self):
        """Handle receivable/payable accounts only change."""
        partners_id = []
        cr = self.env.cr
        if self.customers or self.suppliers:
            if self.customers and self.suppliers:
                cr.execute(
                    "SELECT distinct partner_id FROM account_move_line as l "
                    "INNER JOIN account_account a on a.id = l.account_id "
                    " where a.internal_type = 'receivable' OR a.internal_type = 'payable' "
                    "and a.company_id = %s", (self.company_id.id,))
            elif self.customers:
                cr.execute(
                    "SELECT distinct partner_id FROM account_move_line as l "
                    "INNER JOIN account_account a on a.id = l.account_id "
                    " where a.internal_type = 'receivable' "
                    "and a.company_id = %s", (self.company_id.id,))
            elif self.suppliers:
                cr.execute(
                    "SELECT distinct partner_id FROM account_move_line as l "
                    "INNER JOIN account_account a on a.id = l.account_id "
                    " where a.internal_type ='payable' "
                    "and a.company_id = %s", (self.company_id.id,))
            partner_ids = cr.fetchall()
            for partner in partner_ids:
                partners_id.append(partner[0])
            self.partner_ids = self.env['res.partner'].browse(partners_id)
            print('ggggééééééé', self.partner_ids)
        else:
            self.partner_ids = None

    def _export(self, xlsx_report=False):
        """Default export is PDF."""
        model = self.env['report_general_ledger_qweb']
        report = model.create(self._prepare_report_general_ledger())
        return report.print_report(xlsx_report)

    # @api.multi
    def button_export_gl(self):
        self.ensure_one()
        return self.env.ref('account_financial_report_ma.financial_report_gl_xlsx').report_action(self)

    # @api.multi
    def button_export_balance(self):
        self.ensure_one()
        return self.env.ref('account_financial_report_ma.financial_report_balance_xlsx').report_action(self)
