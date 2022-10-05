# -*- coding: utf-8 -*-

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools import float_compare, float_is_zero
import math


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    asset_id = fields.Many2one('account.asset.asset','Immobilisation')

    # @api.multi
    def invoice_validate(self):
        for invoice in self:
            # refuse to validate a vendor bill/refund if there already exists one with the same reference for the same partner,
            # because it's probably a double encoding of the same bill/refund
            if invoice.move_type in ('in_invoice', 'in_refund') and invoice.reference:
                if self.search([('move_type', '=', invoice.move_type), ('reference', '=', invoice.reference),
                                ('company_id', '=', invoice.company_id.id),
                                ('commercial_partner_id', '=', invoice.commercial_partner_id.id),
                                ('id', '!=', invoice.id)]):
                    raise UserError(_(
                        "Duplicated vendor reference detected. You probably encoded twice the same vendor bill/refund."))
            if invoice.asset_id:
                invoice.move_id.write({'asset_id':invoice.asset_id.id})
                invoice.asset_id.write({'sold_amount':invoice.amount_untaxed})
        return self.write({'state': 'open'})


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('asset_category_id')
    def onchange_asset(self):
        if self.asset_category_id:
            self.property_account_expense_id = self.asset_category_id.account_immo_id
            self.property_account_income_id = self.asset_category_id.account_revenue_id


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    account_immo_id = fields.Many2one('account.account', string="Compte d'immobilisation", required=True, domain=[('internal_type','=','other'), ('deprecated', '=', False)])
    account_vna_id = fields.Many2one('account.account', string="Compte VNA", required=False, domain=[('internal_type','=','other'), ('deprecated', '=', False)])
    account_revenue_id = fields.Many2one('account.account', string="Compte de produit de cession", required=False, domain=[('internal_type','=','other'), ('deprecated', '=', False)])
    ref_debit_credit  = fields.Char(string='Référence d\'importation')


class AccountAsset(models.Model):
    _inherit = "account.asset.asset"

    invoice_date = fields.Date(string=u"Date de facturation", required=True)
    is_cost_asset = fields.Boolean(u'Charge à répartir sur plusieurs exercice')
    is_depreciated = fields.Boolean(u'Le bien est amorti',default=True)
    parent_id = fields.Many2one('account.asset.asset', string=u'Immo Parent')
    child_ids = fields.One2many(inverse_name='parent_id',string=u'Immo Childs', comodel_name='account.asset.asset')
    acquisition_mode = fields.Selection([('a', 'Acquisition'),
                                         ('p', 'Production'),
                                         ('v', 'Virement')],
                                       u"Mode d'acquisition", required=True, default='a')
    serial_number = fields.Char(u'Code / Numéro de série')
    first_depriaction_value = fields.Float(string='Valeur d\'amortissement antérieure')
    date_depriaction_value  = fields.Date(string='Date d\'amortissement antérieure')

    cumul_amortissements_anterieurs = fields.Float(u'Amortissements antérieurs',
                                                   help=u"Il s'agit du cumul des amortissements calculés antiérerement au transfert des immobilisations au système")
    cumul_amortissements = fields.Float(u'Cumul des amortissements', compute='_compute_cumul_amortissements')

    #Champs cession
    
    tva  = fields.Many2one('account.tax',string='TVA')
    cession_price_ttc  = fields.Float(string='Prix de cession',compute="_compute_cession_price_ttc", store=True)
    mode_session = fields.Selection([('c', 'Cession'),
                                     ('r', 'Retrait'),
                                     ('v', 'Virement')],
                                       u"Mode de cession", required=True, default='c')
    
    cession_price_ht  = fields.Float(string='Prix de cession HT')
    date_cession = fields.Date('Date de cession')
    vna_move_id = fields.Many2one('account.move', u'Pièce comptable VNA', readonly=True)
    amount_vna = fields.Float(u'Valeur VNA', readonly=True)
    sold_amount = fields.Float(u'Montant de cession', readonly=True)
    reeval_value = fields.Float(u'Valeur comptable après réévaluation')
    observations = fields.Text(u'Observations')

    asset_succursale_id = fields.Many2one(comodel_name="asset.succursale", string=u"Succursale", required=False, )
    asset_emplacement_id = fields.Many2one(comodel_name="asset.emplacement", string=u"Emplacement", required=False, )

    related_customer_invoice_id = fields.Many2one(string='Facture Client', comodel_name='account.move', domain=[('move_type', '=', 'out_invoice')])

    @api.onchange('related_customer_invoice_id')
    def onchange_related_customer_invoice_id(self):
        for rec in self:
            if rec.related_customer_invoice_id:
                for move in rec.related_customer_invoice_id:
                    rec.date_cession = move.invoice_date
                    for line in move.invoice_line_ids:
                        rec.cession_price_ht += line.price_subtotal 

    # @api.one
    @api.depends('cumul_amortissements_anterieurs', 'depreciation_line_ids.amount')
    def _compute_cumul_amortissements(self):
        self.ensure_one()
        total_amount = 0.0
        for line in self.depreciation_line_ids:
            if line.move_check and line.depreciation_date < fields.Date.context_today(self):
                total_amount += line.amount
        self.cumul_amortissements = self.cumul_amortissements_anterieurs + total_amount
    
    @api.depends('tva','cession_price_ht')
    def _compute_cession_price_ttc(self):
        for rec in self:
            if rec.tva:
                for field in rec.tva:
                    rec.cession_price_ttc = rec.cession_price_ht + ((rec.cession_price_ht * field.amount) / 100)


    # @api.one
    @api.depends('value', 'salvage_value', 'depreciation_line_ids.move_check', 'depreciation_line_ids.amount', 'cumul_amortissements_anterieurs')
    def _amount_residual(self):
        for rec in self:
            # self.ensure_one()
            total_amount = 0.0
            for line in rec.depreciation_line_ids:
                if line.move_check:
                    total_amount += line.amount
            rec.value_residual = rec.value - total_amount - rec.salvage_value - rec.cumul_amortissements_anterieurs

    # @api.multi
    def _compute_entries(self, date, group_entries=False):
        current_date_range = self.env.user.company_id.find_daterange_fy(fields.Date.from_string(date))
        depreciation_ids = self.env['account.asset.depreciation.line'].search([
            ('asset_id', 'in', self.ids), ('depreciation_date', '<=', date), ('depreciation_date', '>=', current_date_range.date_start),
            ('move_check', '=', False), ('asset_id.is_depreciated', '=', True)])
        if group_entries:
            return depreciation_ids.create_grouped_move()
        return depreciation_ids.create_move()

    @api.model
    def compute_generated_entries(self, date, asset_type=None):
        # Entries generated : one by grouped category and one by asset from ungrouped category
        created_move_ids = []
        type_domain = []
        if asset_type:
            type_domain = [('type', '=', asset_type)]

        ungrouped_assets = self.env['account.asset.asset'].search(
            type_domain + [('state', '=', 'open'), ('category_id.group_entries', '=', False)])
        if ungrouped_assets:
            created_move_ids += ungrouped_assets._compute_entries(date, group_entries=False)

        for grouped_category in self.env['account.asset.category'].search(type_domain + [('group_entries', '=', True)]):
            assets = self.env['account.asset.asset'].search(
                [('state', '=', 'open'), ('category_id', '=', grouped_category.id)])
            if assets:
                created_move_ids += assets._compute_entries(date, group_entries=True)
        return created_move_ids

    def generate_cession_move(self):
        '''This function generate account move for cession from assets'''
        company_currency = self.company_id.currency_id
        current_currency = self.currency_id
        sign = (self.category_id.journal_id.type == 'purchase' or self.category_id.journal_id.type == 'sale' and 1) or -1
        categ_type = self.category_id.type
        debitor_account = self.env['account.account'].search([('code','=like','3481%')],limit=1)
        move_line_1 = {
            'name': self.name,
            'account_id': self.category_id.account_revenue_id.id,
            'debit': 0,
            'credit': self.cession_price_ht,
            'journal_id': self.category_id.journal_id.id,
            'partner_id': self.partner_id.id,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
            'analytic_account_id': line.asset_id.category_id.account_analytic_id.id if categ_type == 'sale' else False,
            'date': self.date_cession,
        }
        move_line_2 = {
            'name': self.name,
            'account_id': debitor_account.id,
            'debit': self.cession_price_ht,
            'credit': 0,
            'journal_id': self.category_id.journal_id.id,
            'partner_id': self.partner_id.id,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
            'analytic_account_id': line.asset_id.category_id.account_analytic_id.id if categ_type == 'sale' else False,
            'date': self.date_cession,
        }
        move_vals = {
            'ref': self.code,
            'date': self.date_cession or False,
            'journal_id': self.category_id.journal_id.id,
            'asset_id' : self.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        move = self.env['account.move'].create(move_vals)
        return [move]

    def generate_vna_move(self):
        company_currency = self.company_id.currency_id
        current_currency = self.currency_id
        sign = (self.category_id.journal_id.type == 'purchase' or self.category_id.journal_id.type == 'sale' and 1) or -1
        categ_type = self.category_id.type
        amonut_dep =  0
        for line in self.depreciation_line_ids:
            amonut_dep+=line.amount
        amount_vna = self.value - amonut_dep
        move_line_1 = {
            'name': self.name,
            'account_id': self.category_id.account_vna_id.id,
            'debit': amount_vna,
            'credit': 0,
            'journal_id': self.category_id.journal_id.id,
            'partner_id': self.partner_id.id,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
            'analytic_account_id': line.asset_id.category_id.account_analytic_id.id if categ_type == 'sale' else False,
            'date': self.date_cession,
        }
        move_line_2 = {
            'name': self.name,
            'account_id': self.category_id.account_asset_id.id,
            'debit': amonut_dep,
            'credit': 0,
            'journal_id': self.category_id.journal_id.id,
            'partner_id': self.partner_id.id,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
            'analytic_account_id': line.asset_id.category_id.account_analytic_id.id if categ_type == 'sale' else False,
            'date': self.date_cession,
        }
        move_line_3 = {
            'name': self.name,
            'account_id': self.category_id.account_immo_id.id,
            'debit': 0,
            'credit': self.value,
            'journal_id': self.category_id.journal_id.id,
            'partner_id': self.partner_id.id,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
            'analytic_account_id': line.asset_id.category_id.account_analytic_id.id if categ_type == 'sale' else False,
            'date': self.date_cession,
        }
        move_vals = {
            'ref': self.code,
            'date': self.date_cession or False,
            'journal_id': self.category_id.journal_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2),(0, 0, move_line_3)],
            'asset_id': self.id,
        }
        move = self.env['account.move'].create(move_vals)
        return [move,amount_vna]

    def _compute_board_amount(self, sequence, residual_amount, amount_to_depr, undone_dotation_number,
                              posted_depreciation_line_ids, total_days, depreciation_date):
        amount = 0
        if sequence == undone_dotation_number:
            amount = residual_amount
        else:
            if self.method == 'linear':
                amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids))
                if self.prorata and self.category_id.type == 'purchase':
                    amount = amount_to_depr / self.method_number
                    if sequence == 1:
                        # print "depreciation_date",depreciation_date.month
                        months = 13 - depreciation_date.month
                        amount = (amount_to_depr / self.method_number) / 12 * months
            elif self.method == 'degressive':
                amount = residual_amount * self.method_progress_factor
                if self.prorata:
                    if sequence == 1:
                        months = 13 - depreciation_date.month
                        amount = (residual_amount * self.method_progress_factor) / 12 * months
        return amount

    def compute_depreciation_board(self):
        self.ensure_one()

        posted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: x.move_check).sorted(
            key=lambda l: l.depreciation_date, reverse=True)
        unposted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: not x.move_check)

        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

        if self.value_residual != 0.0 and not self.vna_move_id and self.first_depriaction_value > 0 and self.date_depriaction_value:
            
            amount_to_depr = self.value_residual 
            residual_amount = self.value_residual
            date_dep = datetime.strptime(str(self._get_last_depreciation_date()[self.id]), DF).date()
            if self.prorata:
                depreciation_date = datetime.strptime(str(date_dep.year) + '-12-31',
                                                      DF).date()
            else:
                # depreciation_date = 1st of January of purchase year
                if self.method_period >= 12:
                    asset_date = datetime.strptime(str(self.date.year) + '-12-31', DF).date()
                else:
                    asset_date = datetime.strptime(self.date[:7] + '-01', DF).date()

                    # date_asset = fields.Date.from_string(self.date)
                    # asset_date = datetime(date_asset.year, date_asset.month, 1) + relativedelta(months=1)
                # if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
                if posted_depreciation_line_ids and posted_depreciation_line_ids[0].depreciation_date:
                    last_depreciation_date = datetime.strptime(posted_depreciation_line_ids[0].depreciation_date,
                                                               DF).date()
                    depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)

                else:
                    depreciation_date = asset_date
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366

            undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)

            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                sequence = x + 1
                amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr, undone_dotation_number,
                                                    posted_depreciation_line_ids, total_days, date_dep)
                amount = self.currency_id.round(amount)
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                if depreciation_date.year == self.date_depriaction_value.year:
                    residual_amount -= amount
                    
                    vals = {
                        'amount': amount,
                        'asset_id': self.id,
                        'sequence': sequence,
                        'name': (self.code or '') + '/' + str(sequence),
                        'remaining_value': residual_amount,
                        'depreciated_value': self.first_depriaction_value,
                        'depreciation_date': depreciation_date.strftime(DF),
                    }
                    commands.append((0, False, vals))
                    # Considering Depr. Period as months
                    depreciation_date = date(year, month, day) + relativedelta(months=+self.method_period)
                    day = depreciation_date.day
                    month = depreciation_date.month
                    year = depreciation_date.year
                else:
                    residual_amount -= amount
                    if self.value - (self.salvage_value + residual_amount) < self.value:
                        vals = {
                            'amount': amount ,
                            'asset_id': self.id,
                            'sequence': sequence,
                            'name': (self.code or '') + '/' + str(sequence),
                            'remaining_value': residual_amount,
                            'depreciated_value': self.value - (self.salvage_value + residual_amount),
                            'depreciation_date': depreciation_date.strftime(DF),
                        }
                        commands.append((0, False, vals))
                        # Considering Depr. Period as months
                        depreciation_date = date(year, month, day) + relativedelta(months=+self.method_period)
                        day = depreciation_date.day
                        month = depreciation_date.month
                        year = depreciation_date.year
                    else:
                        vals = {
                            'amount':residual_amount + amount ,
                            'asset_id': self.id,
                            'sequence': sequence,
                            'name': (self.code or '') + '/' + str(sequence),
                            'remaining_value': 0,
                            'depreciated_value': self.value,
                            'depreciation_date': depreciation_date.strftime(DF),
                        }
                        commands.append((0, False, vals))
                        # Considering Depr. Period as months
                        depreciation_date = date(year, month, day) + relativedelta(months=+self.method_period)
                        day = depreciation_date.day
                        month = depreciation_date.month
                        year = depreciation_date.year
                        break
        if self.value_residual != 0.0 and not self.vna_move_id and self.first_depriaction_value == 0 and not self.date_depriaction_value:
            amount_to_depr = residual_amount = self.value_residual
            date_dep = datetime.strptime(str(self._get_last_depreciation_date()[self.id]), DF).date()
            if self.prorata:
                depreciation_date = datetime.strptime(str(date_dep.year) + '-12-31',
                                                    DF).date()
            else:
                # depreciation_date = 1st of January of purchase year
                if self.method_period >= 12:
                    asset_date = datetime.strptime(str(self.date.year) + '-12-31', DF).date()
                else:
                    asset_date = datetime.strptime(self.date[:7] + '-01', DF).date()

                    # date_asset = fields.Date.from_string(self.date)
                    # asset_date = datetime(date_asset.year, date_asset.month, 1) + relativedelta(months=1)
                # if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
                if posted_depreciation_line_ids and posted_depreciation_line_ids[0].depreciation_date:
                    last_depreciation_date = datetime.strptime(posted_depreciation_line_ids[0].depreciation_date,
                                                            DF).date()
                    depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)

                else:
                    depreciation_date = asset_date
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366

            undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)

            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                sequence = x + 1
                amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr, undone_dotation_number,
                                                    posted_depreciation_line_ids, total_days, date_dep)
                amount = self.currency_id.round(amount)
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                residual_amount -= amount
                vals = {
                    'amount': amount,
                    'asset_id': self.id,
                    'sequence': sequence,
                    'name': (self.code or '') + '/' + str(sequence),
                    'remaining_value': residual_amount,
                    'depreciated_value': self.value - (self.salvage_value + residual_amount),
                    'depreciation_date': depreciation_date.strftime(DF),
                }
                commands.append((0, False, vals))
                # Considering Depr. Period as months
                depreciation_date = date(year, month, day) + relativedelta(months=+self.method_period)
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year
        self.write({'depreciation_line_ids': commands})

        return True
    # @api.multi
    def set_to_close(self):
        move_ids = []
        for asset in self:
            unposted_depreciation_line_ids = asset.depreciation_line_ids.filtered(lambda x: not x.move_check)
            if unposted_depreciation_line_ids:
                old_values = {
                    'method_end': asset.method_end,
                    'method_number': asset.method_number,
                }

                # Remove all unposted depr. lines
                commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

                # Create a new depr. line with the residual amount and post it
                sequence = len(asset.depreciation_line_ids) - len(unposted_depreciation_line_ids) + 1
                date_cession = self.date_cession
                if not date_cession :
                    raise ValidationError(
                        (u'Merci de préciser la date et la méthode de cession.'))
                if self.method_number == 0 :
                    raise ValidationError(
                        (u'Merci de préciser le nombre de depreciation.'))
                else:
                    depreciation_date = datetime.strptime(str(date_cession.year) + '-12-31', DF).date()
                    date_split =str(self.date)
                    date_split = date_split.split('-')
                    last_date = date(int(date_split[0]), int(date_split[1]),int(date_split[2]))+relativedelta(years=int(self.method_number))
                    date_cession_split = str(date_cession)
                    date_cession_split = date_cession_split.split('-')
                    diff = (last_date- date(int(date_cession_split[0]), int(date_cession_split[1]),int(date_cession_split[2])))
                    diff_dep_date = depreciation_date - date(int(date_cession_split[0]), int(date_cession_split[1]),int(date_cession_split[2]))
                    amount = 0
                    if diff>diff_dep_date:
                        months = int(date_cession_split[1])-1
                        amount = (self.value - self.first_depriaction_value / self.method_number) / 12 * months
                    else:
                        diff = str(diff)
                        diff = diff.split(' ')
                        months = math.floor(float(diff[0])/60)
                        amount = (self.value - self.first_depriaction_value / self.method_number) / 12 * months
                    vals = {
                        'amount': amount,
                        'asset_id': asset.id,
                        'sequence': sequence,
                        'name': (asset.code or '') + '/' + str(sequence) + u'(Dotation complémentaire)',
                        'remaining_value': 0,
                        'depreciated_value': asset.value - asset.salvage_value,  # the asset is completely depreciated
                        'depreciation_date': depreciation_date,
                    }
                    commands.append((0, False, vals))
                    asset.write({'depreciation_line_ids': commands, 'method_end': asset.method_end, 'method_number': sequence})
                    tracked_fields = self.env['account.asset.asset'].fields_get(['method_number', 'method_end'])
                    changes, tracking_value_ids = asset._mail_track(tracked_fields, old_values) #i modify here 
                    if changes:
                        asset.message_post(subject=_('Asset sold or disposed. Accounting entry awaiting for validation.'),
                                        tracking_value_ids=tracking_value_ids)
                    move_ids += asset.depreciation_line_ids[-1].create_move(post_move=False)
                    move_id = self.generate_vna_move()
                    self.generate_cession_move()
                    self.write({'vna_move_id': move_id[0].id,'state': 'close','amount_vna':move_id[1],'value_residual':0})

class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    # @api.multi
    def create_move(self, post_move=True):
            created_moves = self.env['account.move']
            for line in self:
                if line.move_id:
                    raise UserError(
                        ('This depreciation is already linked to a journal entry! Please post or delete it.'))
                depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
                company_currency = line.asset_id.company_id.currency_id
                current_currency = line.asset_id.currency_id
                amount = current_currency.compute(line.amount, company_currency)
                sign = (line.asset_id.category_id.journal_id.type == 'purchase' or line.asset_id.category_id.journal_id.type == 'sale' and 1) or -1
                asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, line.asset_id.method_number)
                reference = line.asset_id.code
                journal_id = line.asset_id.category_id.journal_id.id
                partner_id = line.asset_id.partner_id.id
                categ_type = line.asset_id.category_id.type
                credit_account = line.asset_id.category_id.account_asset_id.id
                debit_account = line.asset_id.category_id.account_depreciation_id.id
                move_line_1 = {
                    'name': asset_name,
                    'account_id': credit_account,
                    'debit': 0.0,
                    'credit': amount,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
                    'analytic_account_id': line.asset_id.category_id.account_analytic_id.id if categ_type == 'sale' else False,
                    'date': depreciation_date,
                }
                move_line_2 = {
                    'name': asset_name,
                    'account_id': debit_account,
                    'credit': 0.0,
                    'debit': amount,
                    'journal_id': journal_id,
                    'partner_id': partner_id,
                    'currency_id': company_currency != current_currency and current_currency.id or False,
                    'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
                    'analytic_account_id': line.asset_id.category_id.account_analytic_id.id if categ_type == 'purchase' else False,
                    'date': depreciation_date,
                }
                move_vals = {
                    'ref': reference,
                    'date': depreciation_date or False,
                    'journal_id': line.asset_id.category_id.journal_id.id,
                    'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
                    'asset_id': line.asset_id.id,
                    }
                move = self.env['account.move'].create(move_vals)
                line.write({'move_id': move.id, 'move_check': True})
                created_moves |= move

            if post_move and created_moves:
                created_moves.filtered(lambda r: r.asset_id and r.asset_id.category_id and r.asset_id.category_id.open_asset).post()
            return [x.id for x in created_moves]

class AssetSuccursale(models.Model):
    _name = 'asset.succursale'

    name = fields.Char(string=u"Succursale",required=True)
    itp = fields.Char(string=u'Identifiant Taxe Professionnelle')


class AccountMove(models.Model):
    _inherit = 'account.move'

    asset_id = fields.Many2one('account.asset.asset', string='Immobilisation', ondelete="restrict")


class AssetEmplacement(models.Model):
    _name = 'asset.emplacement'

    name = fields.Char(string=u"Emplacement d'affectation",required=True)
    succursale_id = fields.Many2one(comodel_name="asset.succursale", string=u"Succursale", required=True)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    # @api.one
    def asset_create(self):
        self.ensure_one()
        if self.asset_category_id:
            vals = {
                'name': self.name,
                'code': self.invoice_id.number or False,
                'category_id': self.asset_category_id.id,
                'value': self.price_subtotal_signed,
                'partner_id': self.invoice_id.partner_id.id,
                'company_id': self.invoice_id.company_id.id,
                'currency_id': self.invoice_id.company_currency_id.id,
                'date': self.invoice_id.date_invoice,
                'invoice_id': self.invoice_id.id,
                'invoice_date':self.invoice_id.date_invoice
            }
            changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
            vals.update(changed_vals['value'])
            asset = self.env['account.asset.asset'].create(vals)
            if self.asset_category_id.open_asset:
                asset.validate()
        return True