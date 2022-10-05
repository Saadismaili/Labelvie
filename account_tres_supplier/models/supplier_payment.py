# -*- coding: utf-8 -*-

from odoo import models,fields, api
from odoo.exceptions import ValidationError


class SupplierPayment(models.Model):
    _name = "supplier.payment"
    _description = "Reglement Fournisseur"
    _inherit = ['mail.thread']
    _order = "date desc"

    def get_model(self, type):
        res = False
        if type == 'effet':
            model_ids = self.env['paiement.effet.model.supplier'].search([])
            if model_ids:
                res = model_ids.id
        return res

    def action_valide(self):
        for record in self:
            record.state = 'valide'

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def prepare_line_vals(self, record_line):
        company_id=self.env.user.company_id.id

        vals = {
            'name': record_line.paiement_ref,
            'amount': record_line.montant,
            # 'montant_devise': record_line.montant_devise,
            'journal_id': record_line.journal_id.id,
            'date': record_line.supplier_payment_id.date,
            'partner_id': record_line.supplier_payment_id.partner_id.id,
            'period_id': record_line.supplier_payment_id.period_id.id,
            'company_id': company_id,
            'supplier_payment_id': record_line.supplier_payment_id.id,
            'note': self.get_invoices(),
        }
        return vals

    def create_acc_doc(self, record_line):
        effet_supplier_obj = self.env['paiement.effet.supplier']
        cheque_supplier_obj = self.env['paiement.cheque.supplier']
        ov_supplier_obj = self.env['paiement.ov.supplier']
        cash_supplier_obj = self.env['paiement.cash.supplier']
        company_id=self.env.user.company_id.id

        vals = self.prepare_line_vals(record_line)

        if record_line.type == 'cash':
            vals['name'] = '/'
            cash_id = cash_supplier_obj.create(vals)
            return cash_id

        if record_line.type == 'effet':
            vals['model_id'] = self.get_model('effet')
            vals['due_date'] = record_line.due_date
            effet_id = effet_supplier_obj.create(vals)
            effet_id.button_delivred()
            return effet_id

        if record_line.type == 'cheque':
            vals['due_date'] = record_line.due_date
            cheque_id = cheque_supplier_obj.create(vals)
            cheque_id.button_envoyer()
            return cheque_id

        if record_line.type == 'ov':
            ov_id = ov_supplier_obj.create(vals)
            vals['due_date'] = record_line.due_date
            return ov_id

    def action_done(self):
        for record in self:
            for line in record.supplier_payment_line_ids:
                self.create_acc_doc(line)
            record.state = 'done'
        return True

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('supplier_payment')
        res = super(SupplierPayment, self).create(vals)
        return res

    def get_invoices(self):
        note = ''
        for record in self:
            for line in record.invoice_ids:
                note += line.number + '-'
        return note

    @api.onchange('date')
    def onchange_period_id(self):
        period_id = False
        period_obj = self.env['date.range']
        periods = period_obj.search([('date_start', '<=', self.date),('date_end', '>=', self.date)])
        if periods:
            period_id = periods[0]
        self.period_id = period_id

    def action_draft(self):
        for rec in self:
            rec.cheque_lines.unlink()
            rec.effet_lines.unlink()
            rec.ov_lines.unlink()
            rec.cash_lines.unlink()
            rec.write({'state': 'draft'})

    name = fields.Char(u"Numéro",readonly=True)
    date = fields.Date(u'Date',default=fields.Date.context_today,readonly=True,states={'draft':[('readonly', False)]})
    partner_id = fields.Many2one('res.partner', u'Fournisseur', required=True,readonly=True,states={'draft':[('readonly', False)]})
    demandeur_interne_id = fields.Many2one('res.users', u'Demandeur',readonly=True,states={'draft':[('readonly', False)]})
    motif = fields.Text(u"Motif",readonly=True,states={'draft':[('readonly', False)]})
    period_id = fields.Many2one('date.range', u'Période', required=True,readonly=True,states={'draft':[('readonly', False)]})
    journal_id = fields.Many2one('account.journal', u'Journal', required=False, readonly=True,
                                 states={'draft': [('readonly', False)]}, domain=[('type', 'in', ('bank', 'cash'))])
    cheque_lines = fields.One2many('paiement.cheque.supplier', 'supplier_payment_id', u'Chèques', readonly=True)
    effet_lines = fields.One2many('paiement.effet.supplier', 'supplier_payment_id', u'Effets', readonly=True)
    ov_lines = fields.One2many('paiement.ov.supplier', 'supplier_payment_id', u'OV', readonly=True)
    cash_lines = fields.One2many('paiement.cash.supplier', 'supplier_payment_id', u'Espèces', readonly=True)
    supplier_payment_line_ids = fields.One2many('supplier.payment.line', 'supplier_payment_id', u'Lignes de Paiement', readonly=True,states={'draft':[('readonly', False)]})
    type_reglement = fields.Selection([('normal', u'Normal'),
                                       ('avance', u'Par avance'),
                                       ('certification', u'Certification')], default='normal', string=u'Type de règlement', readonly=True,states={'draft':[('readonly', False)]})
    invoice_ids = fields.Many2many('account.move', 'paiement_supplier_invoice_rel', 'paiement_record_id','invoice_id', u'Factures',readonly=True,states={'draft':[('readonly', False)]})
    company_id = fields.Many2one('res.company', u'Société', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get('supplier.payment'))
    total_amount = fields.Float('Total', compute='_compute_total_amount', store=True)
    state = fields.Selection([('draft', 'Brouillon'),
                                ('valide', u'Validé'),
                               ('done', u'Envoyé'),
                               ('cancel', u'Annulé')],default='draft', string=u'Statut',track_visibility='onchange')

    @api.depends('supplier_payment_line_ids', 'supplier_payment_line_ids.montant')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount =  sum(rec.supplier_payment_line_ids and rec.supplier_payment_line_ids.mapped('montant'))


class SupplierPaymentLine(models.Model):
    _name="supplier.payment.line"
    _description = "Ligne reglement fournisseur"

    @api.constrains('paiement_ref')
    def _check_unique_paiement_ref(self):
        for rec in self:
            list_ids=self.search([('id', '!=', rec.id),
                                  ('paiement_ref', '=', rec.paiement_ref),
                                  ('paiement_ref', '!=', False)])
            if list_ids:
                raise ValidationError(U"Référence existante!")

    type = fields.Selection([
                            ('cash', u'Espèce'),
                            ('effet', u'Effet'),
                            ('cheque', u'Chèque'),
                            ('ov', 'OV')], u'Méthode de Paiement', required=True)
    montant = fields.Float(u"Montant")
    journal_id = fields.Many2one('account.journal', u'Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    montant_devise = fields.Float(u"Montant en devise")
    paiement_ref = fields.Char(u'Référence de Paiement')
    due_date = fields.Date(u"Date d'échéance")
    supplier_payment_id = fields.Many2one(comodel_name="supplier.payment", string=u"Réglement Fournisseur", ondelete="cascade")
