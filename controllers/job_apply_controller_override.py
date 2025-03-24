# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class WebsiteJobControllerCustom(http.Controller):

    @http.route("/jobs/apply/<model('hr.job'):job>", type='http', auth="public", website=True, sitemap=True)
    def jobs_apply(self, job, **kwargs):
        # Si l'utilisateur est connecté (non-public), on vérifie s'il est un candidat
        if not request.env.user._is_public():
            candidat = request.env['website.user'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if candidat:
                # Auto-postulation pour le candidat connecté
                request.env['hr.applicant'].sudo().create({
                    'job_id': job.id,
                    'partner_name': candidat.name,
                    'email_from': candidat.email,
                    'candidat_id': candidat.id,
                    'name': f"Candidature de {candidat.name} pour {job.name}",
                })
                return request.redirect('/mon-espace')

        # Sinon (public user ou non-candidat), on affiche le formulaire standard
        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')

        return request.render("website_hr_recruitment.apply", {
            'job': job,
            'error': error,
            'default': default,
        })
