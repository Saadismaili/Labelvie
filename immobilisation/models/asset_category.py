import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero


class AccountAssetCategoryInherit(models.Model):
    _inherit = 'account.asset.category'

    account_type = fields.Selection(string='Type', selection=[('1', '* Frais préliminaires'),('2', '* Charges à répartir sur plusieurs exercices'),('0', '* Primes de remboursement obligations')
                                                        ,('3', '* Immobilisation en recherche et développement'),('4', '* Brevets, marques droits et valeurs similairest')
                                                        ,('5', '* Fonds commercial'),('6', '* Autres immobilisations incorporelles')
                                                        ,('7', '* Terrains'),('8', '* Constructions')
                                                        ,('9', '* Installations techniques; matériel et outillage'),('10', '* Matériel de transport')
                                                        ,('11', '* Mobilier, matériel de bureau et aménagements	'),('12', '* Autres immobilisations corporelles')
                                                        ,('13', '* Immobilisations corporelles en cours'),('14', '* Autre')],default='14',required=True, )