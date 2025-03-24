# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CandidatProfileAdditions(http.Controller):

    @http.route('/mon-espace/ajouter/experience', type='http', auth='user', website=True)
    def ajouter_experience_form(self, **kw):
        return request.render('website_bensizwe.ajouter_experience_template')

    @http.route('/mon-espace/ajouter/experience/submit', type='http', auth='user', website=True, methods=['POST'])
    def ajouter_experience_submit(self, **post):
        candidat = request.env['website.user'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if candidat:
            request.env['website.experience'].sudo().create({
                'name': post.get('name'),
                'description': post.get('description'),
                'date_start': post.get('date_start'),
                'date_end': post.get('date_end'),
                'candidat_id': candidat.id
            })
        return request.redirect('/mon-espace')

    @http.route('/mon-espace/ajouter/education', type='http', auth='user', website=True)
    def ajouter_education_form(self, **kw):
        return request.render('website_bensizwe.ajouter_education_template')

    @http.route('/mon-espace/ajouter/education/submit', type='http', auth='user', website=True, methods=['POST'])
    def ajouter_education_submit(self, **post):
        candidat = request.env['website.user'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if candidat:
            request.env['website.education'].sudo().create({
                'name': post.get('name'),
                'description': post.get('description'),
                'date_start': post.get('date_start'),
                'date_end': post.get('date_end'),
                'candidat_id': candidat.id
            })
        return request.redirect('/mon-espace')

    @http.route('/mon-espace/ajouter/langage', type='http', auth='user', website=True)
    def ajouter_langage_form(self, **kw):
        return request.render('website_bensizwe.ajouter_langage_template')

    @http.route('/mon-espace/ajouter/langage/submit', type='http', auth='user', website=True, methods=['POST'])
    def ajouter_langage_submit(self, **post):
        candidat = request.env['website.user'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if candidat and post.get('name'):
            langage = request.env['website.langage'].sudo().search([('name', '=', post.get('name'))], limit=1)
            if not langage:
                langage = request.env['website.langage'].sudo().create({
                    'name': post.get('name'),
                    'description': post.get('description'),
                })
            candidat.write({'langage_ids': [(4, langage.id)]})
        return request.redirect('/mon-espace')
