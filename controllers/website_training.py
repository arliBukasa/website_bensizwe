from odoo import http
from odoo.http import request
import logging

class WebsiteTrainingController(http.Controller):

    @http.route('/formations/liste', type='json', auth='public')
    def get_paginated_trainings(self, page=1, per_page=6):
        offset = (page - 1) * per_page
        trainings = request.env['website.training'].sudo().search([("is_published","=",True)], offset=offset, limit=per_page)
        total = request.env['website.training'].sudo().search_count([])
        # get the website domain
        domain = request.httprequest.host_url
        logging.info(f"================ Domain: {domain}")
        values = [{
            'name': t.name,
            'description': t.description,
            'date_start': t.date_start,
            'date_end': t.date_end,
            'cout': t.cout,
            'status': t.status,
            'header': t.header,
            'image': t.image,
            'url': '/formation/inscription/' + str(t.id),
            'id': t.id,
        } for t in trainings]
        return {
            'trainings': values,
            'page': page,
            'total_pages': (total + per_page - 1) // per_page,
        }
