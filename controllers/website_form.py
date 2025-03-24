from odoo import http
from odoo.http import request

class CandidatProfileController(http.Controller):

    @http.route('/mon-espace/ajouter/formation', type='http', auth='user', website=True)
    def ajouter_formation_form(self, **kw):
        return request.render('website_bensizwe.ajouter_formation_template', {})

    @http.route('/mon-espace/ajouter/formation/submit', type='http', auth='user', website=True, methods=['POST'])
    def ajouter_formation_submit(self, **post):
        candidat = request.env['website.user'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        if candidat:
            request.env['website.formation'].sudo().create({
                'name': post.get('name'),
                'description': post.get('description'),
                'date_start': post.get('date_start'),
                'date_end': post.get('date_end'),
                'candidat_id': candidat.id
            })
        return request.redirect('/mon-espace')
