from odoo import http
from odoo.http import request

class WebsiteTrainingController(http.Controller):

    @http.route(['/formations/liste'], type='json', auth='public', website=True)
    def get_paginated_trainings(self, page=1, per_page=6):
        offset = (page - 1) * per_page
        trainings = request.env['website.training'].sudo().search([("is_published","=",True)], offset=offset, limit=per_page)
        total = request.env['website.training'].sudo().search_count([])
        values = [{
            'name': t.name,
            'description': t.description,
            'date_start': t.date_start,
            'date_end': t.date_end,
            'cout': t.cout,
            'status': t.status,
            'header': t.header,
            'image': t.image,
            'id': t.id,
        } for t in trainings]
        return {
            'trainings': values,
            'page': page,
            'total_pages': (total + per_page - 1) // per_page,
        }
