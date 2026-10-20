import logging

from odoo import api, SUPERUSER_ID
from odoo.addons.website_bensizwe.models.certificate import (
    DEFAULT_DIRECTOR, DEFAULT_TRAINER, _default_signature)

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {'tracking_disable': True})

    # 1. Formations existantes : signataires par défaut là où rien n'est renseigné (le reste n'est pas touché)
    defaults = {
        'trainer_name': DEFAULT_TRAINER,
        'director_name': DEFAULT_DIRECTOR,
        'trainer_signature': _default_signature('signature_formateur.png'),
        'director_signature': _default_signature('signature_dg.png'),
    }
    trainings = env['website.training'].search([])
    for training in trainings:
        vals = {field: value for field, value in defaults.items() if value and not training[field]}
        if vals:
            training.write(vals)
    _logger.info("website_bensizwe 2.5 : signataires par défaut posés sur %s formation(s)", len(trainings))

    # 2. Certificats déjà délivrés : noms vides -> noms de la formation (pour que les réimpressions les affichent)
    for certificate in env['website.training.certificate'].search(
            ['|', ('trainer_name', '=', False), ('director_name', '=', False)]):
        vals = {}
        if not certificate.trainer_name and certificate.training_id.trainer_name:
            vals['trainer_name'] = certificate.training_id.trainer_name
        if not certificate.director_name and certificate.training_id.director_name:
            vals['director_name'] = certificate.training_id.director_name
        if vals:
            certificate.write(vals)
