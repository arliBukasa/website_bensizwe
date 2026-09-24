from odoo import http
from odoo.http import request


class CertificateVerificationController(http.Controller):

    @http.route(['/certificat/verification', '/certificat/verification/<string:code>'],
                type='http', auth='public', website=True, sitemap=False)
    def certificate_verification(self, code=None, **kwargs):
        Certificate = request.env['website.training.certificate'].sudo()
        code = Certificate.normalize_code(code or kwargs.get('code'))
        certificate = Certificate.search([('code', '=', code)], limit=1) if code else Certificate
        return request.render('website_bensizwe.certificate_verification_page', {
            'code': code,
            'searched': bool(code),
            'certificate': certificate,
        })
