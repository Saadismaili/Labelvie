from odoo import models, fields, api, _   

class ResCompanyInherit(models.Model):
    _inherit = 'res.company'
    
    id_fisc = fields.Char(string=u'Identifiant Fiscal', related='partner_id.id_fisc',store=True)
    rc = fields.Char(string=u'RC', related='partner_id.rc',store=True)
    cnss = fields.Char(string=u'Numéro de la sécurité sociale', related='partner_id.cnss',store=True)
    capital_social = fields.Char(string=u'Capital social', related='partner_id.capital_social',store=True)
    ice = fields.Char(string=u'ICE', related='partner_id.ice',store=True)
    itp = fields.Char(string=u'Identifiant Taxe Professionnelle', related='partner_id.itp',store=True)
    activites = fields.Char(string=u"Profession ou activités exercées", related='partner_id.activites',store=True)
    nationalite = fields.Char(string=u"Nationalité", related='partner_id.nationalite',store=True)
    fax = fields.Char(string=u"Fax", related='partner_id.fax',store=True)
    