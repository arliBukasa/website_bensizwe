from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug

class AppelsOffresController(http.Controller):

    @http.route(['/appels-offres'], type='http', auth='public', website=True)
    def go_appels_offres(self, **kw):
        blog = request.env.ref('website_bensizwe.blog_appels_offres', raise_if_not_found=False)
        if not blog:
            return request.redirect('/blog')
        return request.redirect('/blog/%s' % slug(blog))