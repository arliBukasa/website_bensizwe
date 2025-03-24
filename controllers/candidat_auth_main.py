# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging


class CandidatAuth(http.Controller):

    @http.route('/candidat/login', type='http', auth='public', website=True)
    def candidat_login(self, **post):
        return request.render('website_bensizwe.candidat_login_template', {})

    @http.route('/candidat/login/submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def candidat_login_submit(self, **post):
        login = post.get('login')
        password = post.get('password')

        user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
        try:
            if user:
                uid=request.session.authenticate(request.env.cr.dbname, login, password)
                #request.redirect(self._login_redirect(uid, redirect=None))
                return request.redirect('/mon-espace')
        except Exception:
            pass
        return request.render('website_bensizwe.candidat_login_template', {
            'error': 'Identifiants incorrects'
        })

    @http.route('/candidat/signup', type='http', auth='public', website=True)
    def candidat_signup(self, **post):
        return request.render('website_bensizwe.candidat_signup_template', {})

    @http.route('/candidat/signup/submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def candidat_signup_submit(self, **post):
        name = post.get('name')
        email = post.get('email')
        password = post.get('password')

        existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
        if existing_user:
            return request.render('website_bensizwe.candidat_signup_template', {
                'error': "Un compte avec cet email existe déjà."
            })

        new_user = request.env['res.users'].sudo().create({
            'name': name,
            'login': email,
            'email': email,
            'password': password,
            'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])]
        })

        request.env['website.user'].sudo().create({
            'name': name,
            'email': email,
            'user_id': new_user.id
        })

        logging.info(' ================== new_user: %s', new_user)
        return request.redirect('/candidat/login')
