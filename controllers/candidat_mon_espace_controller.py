# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

class CandidatEspace(http.Controller):

    @http.route('/mon-espace', type='http', auth='public', website=True)
    def espace_candidat(self, **kwargs):
        if request.env.user._is_public():
            return request.redirect('/candidat/login')

        candidat = request.env['website.user'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not candidat:
            return request.redirect('/candidat/signup')

        # Offres non encore postulées
        postes_postules_ids = candidat.application_ids.mapped('job_id').ids
        offres = request.env['hr.job'].sudo().search([
            ('id', 'not in', postes_postules_ids)
        ])

        return request.render('website_bensizwe.candidat_espace_template', {
            'candidat': candidat,
            'offres': offres
        })
    @http.route('/mon-espace/imprimer-cv', type='http', auth='user', website=True)
    def imprimer_cv(self, **kwargs):
        candidat = request.env['website.user'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        if not candidat:
            return request.redirect('/mon-espace')

        report_ref = 'website_bensizwe.report_cv_pdf'
        return request.redirect(f'/report/pdf/{report_ref}/{candidat.id}')

    @http.route('/mon-espace/modifier', type='http', auth='user', website=True)
    def candidat_modifier(self, **kwargs):
        candidat = request.env['website.user'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        return request.render('website_bensizwe.candidat_update_template', {'candidat': candidat})

    @http.route('/mon-espace/actualiser', type='http', auth='user', methods=['POST'], csrf=True, website=True)
    def candidat_modifier_post(self, **post):
        candidat = request.env['website.user'].sudo().browse(int(post.get('candidat_id')))
        if candidat:
            candidat.write({
                'name': post.get('name'),
                'email': post.get('email'),
                'phone': post.get('phone'),
                'nationalite': post.get('nationalite'),
                'adresse': post.get('adresse'),
                'date_naissance': post.get('date_naissance'),
                'etat_civil': post.get('etat_civil'),
            })
        return request.redirect('/mon-espace')