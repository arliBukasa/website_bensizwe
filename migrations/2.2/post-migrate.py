from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Numéros 2.1 (FI-001) -> BSZ-<année de délivrance>-FI-001, même n° d'ordre
    certificates = env['website.training.certificate'].search([('code', 'not like', 'BSZ-%')])
    for certificate in certificates:
        certificate.code = 'BSZ-%s-%s' % (certificate.issue_date.year, certificate.code)
