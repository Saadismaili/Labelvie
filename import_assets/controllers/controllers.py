# -*- coding: utf-8 -*-
# from odoo import http


# class ImportAssets(http.Controller):
#     @http.route('/import_assets/import_assets', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/import_assets/import_assets/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('import_assets.listing', {
#             'root': '/import_assets/import_assets',
#             'objects': http.request.env['import_assets.import_assets'].search([]),
#         })

#     @http.route('/import_assets/import_assets/objects/<model("import_assets.import_assets"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('import_assets.object', {
#             'object': obj
#         })
