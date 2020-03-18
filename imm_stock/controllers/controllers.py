# -*- coding: utf-8 -*-
from odoo import http

# class ImmStock(http.Controller):
#     @http.route('/imm_stock/imm_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/imm_stock/imm_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('imm_stock.listing', {
#             'root': '/imm_stock/imm_stock',
#             'objects': http.request.env['imm_stock.imm_stock'].search([]),
#         })

#     @http.route('/imm_stock/imm_stock/objects/<model("imm_stock.imm_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('imm_stock.object', {
#             'object': obj
#         })