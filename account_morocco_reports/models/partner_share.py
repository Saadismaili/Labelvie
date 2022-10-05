""" init object partner share and lines """

import logging

from odoo import fields, models, api, _
from odoo.exceptions import UserError

LOGGER = logging.getLogger(__name__)


class PartnerShare(models.Model):
    """ init object partner share """
    _name = 'partner.share'
    _description = 'Partner Share'
    _order = 'date desc, id desc'

    def name_get(self):
        """
        Override name Get
        """
        result = []
        for rec in self:
            result.append((rec.id, "Partner Shares Year: %s" % rec.year))
        return result

    # pylint: disable=no-member
    def copy_previous_year_data(self):
        """
        Action Copy previous year data
        """
        self.ensure_one()
        previous = self.search([('year', '=', self.year - 1)],
                               order="year asc", limit=1)
        if previous:
            for line in previous.line_ids:
                line.copy({
                    'partner_share_id': self.id,
                    'partner_shares_previous_year': line.total_partner_shares
                })

    def action_clear_lines(self):
        """
        Action Clear Lines
        """
        self.mapped('line_ids').unlink()

    @api.depends('date')
    def _compute_year(self):
        """
        Compute Year
        """
        for rec in self:
            rec.year = rec.date.year

    @api.depends('line_ids.share_subscribe_value')
    def _compute_total_share_subscribe_value(self):
        """
        Compute total_share_subscribe_value
        """
        for rec in self:
            total_share_subscribe_value = 0
            for line in rec.line_ids:
                total_share_subscribe_value += line.share_subscribe_value
            rec.total_share_subscribe_value = total_share_subscribe_value

    @api.depends('line_ids.share_called_value')
    def _compute_total_share_called_value(self):
        """
        Compute total_share_called_value
        """
        for rec in self:
            total_share_called_value = 0
            for line in rec.line_ids:
                total_share_called_value += line.share_called_value
            rec.total_share_called_value = total_share_called_value

    @api.depends('line_ids.share_paid_value')
    def _compute_total_share_paid_value(self):
        """
        Compute total_share_paid_value
        """
        for rec in self:
            total_share_paid_value = 0
            for line in rec.line_ids:
                total_share_paid_value += line.share_paid_value
            rec.total_share_paid_value = total_share_paid_value

    @api.constrains('year')
    def _constrains_year(self):
        """
        Constrains year
        """
        for rec in self:
            if self.search_count([('year', '=', rec.year),
                                  ('id', '!=', rec.id)]):
                raise UserError(_('The Year: %s Is Already Exist') % rec.year)

    def unlink(self):
        """
        Override unlink to clear the lines.
        """
        self.action_clear_lines()
        return super(PartnerShare, self).unlink()

    date = fields.Date(default=lambda self: fields.Datetime.now(),
                       required=True, )
    year = fields.Integer(compute=_compute_year, store=True)
    line_ids = fields.One2many(comodel_name="partner.share.line",
                               inverse_name="partner_share_id",
                               string="Partner Share Lines", )
    total_share_subscribe_value = fields.Float(
        compute=_compute_total_share_subscribe_value, store=True)
    total_share_called_value = fields.Float(
        compute=_compute_total_share_called_value, store=True)
    total_share_paid_value = fields.Float(
        compute=_compute_total_share_paid_value, store=True)


class PartnerShareLine(models.Model):
    """ init object partner share line """
    _name = 'partner.share.line'
    _description = 'Partner Share Lines'

    @api.depends('total_partner_shares', 'nominal_value')
    def _compute_share_subscribe_value(self):
        """
        Compute share_subscribe_value
        """
        for rec in self:
            share_subscribe_value = rec.total_partner_shares * rec.nominal_value
            rec.share_subscribe_value = share_subscribe_value

    partner_share_id = fields.Many2one(comodel_name="partner.share",
                                       required=True, )
    person = fields.Char()
    company = fields.Char()
    company_number = fields.Char()
    person_number = fields.Char()
    n_ce = fields.Char()
    address = fields.Char()
    partner_shares_previous_year = fields.Float(
        string="Number of Partner Shares Previous Year", readonly=True,
    )
    total_partner_shares = fields.Float(string="Total Number of Partner Shares")
    nominal_value = fields.Float()
    share_subscribe_value = fields.Float(compute=_compute_share_subscribe_value,
                                         store=True)
    share_called_value = fields.Float()
    share_paid_value = fields.Float()
