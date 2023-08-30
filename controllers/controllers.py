# -*- coding: utf-8 -*-
from odoo import http

# class CustomModulo(http.Controller):
#     @http.route('/custom_modulo/custom_modulo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_modulo/custom_modulo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_modulo.listing', {
#             'root': '/custom_modulo/custom_modulo',
#             'objects': http.request.env['custom_modulo.custom_modulo'].search([]),
#         })

#     @http.route('/custom_modulo/custom_modulo/objects/<model("custom_modulo.custom_modulo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_modulo.object', {
#             'object': obj
#         })