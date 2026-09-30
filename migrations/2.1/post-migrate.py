from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # L'ancien paramètre contenait un n° de brevet figé (CD-BSZW-001) : remplacé par
    # website_bensizwe.certificate_arrete, le n° étant désormais celui du certificat
    old_param = env.ref('website_bensizwe.config_certificate_brevet', raise_if_not_found=False)
    if old_param:
        old_param.unlink()

    # Anciens codes aléatoires (BSZ-2026-XXXXXXXX) -> numéro de série par formation (BSZ-2026-FI-001)
    certificates = env['website.training.certificate'].search(
        [('code', '=like', 'BSZ-%')], order='training_id, issue_date, id')
    for certificate in certificates:
        certificate.code = certificate.training_id._next_certificate_code(certificate.issue_date.year)
