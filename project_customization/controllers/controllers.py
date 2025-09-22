# -*- coding: utf-8 -*-
# from odoo import http


# class ProjectCustomization(http.Controller):
#     @http.route('/project_customization/project_customization', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_customization/project_customization/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_customization.listing', {
#             'root': '/project_customization/project_customization',
#             'objects': http.request.env['project_customization.project_customization'].search([]),
#         })

#     @http.route('/project_customization/project_customization/objects/<model("project_customization.project_customization"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_customization.object', {
#             'object': obj
#         })
