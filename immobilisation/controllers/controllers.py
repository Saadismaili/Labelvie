# -*- coding: utf-8 -*-
# from odoo import http


# class Immobilisation(http.Controller):
#     @http.route('/immobilisation/immobilisation', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/immobilisation/immobilisation/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('immobilisation.listing', {
#             'root': '/immobilisation/immobilisation',
#             'objects': http.request.env['immobilisation.immobilisation'].search([]),
#         })

#     @http.route('/immobilisation/immobilisation/objects/<model("immobilisation.immobilisation"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('immobilisation.object', {
#             'object': obj
#         })
