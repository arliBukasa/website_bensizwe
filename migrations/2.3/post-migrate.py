import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

MIGRATION_NOTE = "Reprise 2.3 : participant certifié avant la gestion des paiements."


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'skip_training_sync': True, 'tracking_disable': True})
    Registration = env['website.training.registration']

    # 1. Inscriptions existantes (website.user.training_ids) -> candidats inscrits, source « en ligne »
    cr.execute("""
        SELECT rel.website_user_id, rel.website_training_id, u.create_date::date
          FROM website_training_website_user_rel rel
          JOIN website_user u ON u.id = rel.website_user_id
     LEFT JOIN website_training_registration r
            ON r.candidat_id = rel.website_user_id AND r.training_id = rel.website_training_id
         WHERE r.id IS NULL
    """)
    rows = cr.fetchall()
    Registration.create([{
        'candidat_id': candidat_id,
        'training_id': training_id,
        'registration_date': created,
        'source': 'website',
    } for candidat_id, training_id, created in rows])
    _logger.info("website_bensizwe 2.3 : %s inscription(s) reprise(s)", len(rows))

    # 2. Certificats déjà délivrés -> rattachés à une inscription au statut Participant
    certificates = env['website.training.certificate'].search([('registration_id', '=', False)])
    for certificate in certificates:
        if not certificate.candidat_id:
            _logger.warning("Certificat %s sans candidat : non rattaché à une inscription", certificate.code)
            continue
        registration = Registration.search([
            ('training_id', '=', certificate.training_id.id), ('candidat_id', '=', certificate.candidat_id.id)], limit=1)
        if not registration:
            registration = Registration.create({
                'training_id': certificate.training_id.id, 'candidat_id': certificate.candidat_id.id, 'source': 'fiche'})
        if registration.state != 'confirmed':
            registration.write({'state': 'confirmed', 'note': MIGRATION_NOTE})
        certificate.registration_id = registration

    # 3. Utilisateurs liés à une fiche candidat : accès à « Mes formations » sur le portail
    cr.execute("""
        UPDATE res_users SET is_candidate = TRUE
         WHERE id IN (SELECT user_id FROM website_user WHERE user_id IS NOT NULL)
    """)
