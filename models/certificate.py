import base64
import re
import unicodedata

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

# Mots ignorés pour construire les initiales d'une formation
PREFIX_STOPWORDS = {
    'A', 'AU', 'AUX', 'D', 'DE', 'DES', 'DU', 'EN', 'ENTRE', 'ET', 'L', 'LA', 'LE', 'LES',
    'OU', 'PAR', 'POUR', 'SUR', 'UN', 'UNE', 'DANS', 'AVEC',
}
PREFIX_MAX_WORDS = 4
PREFIX_RE = re.compile(r'^[A-Z0-9]{2,10}$')
CODE_PREFIX = 'BSZ'
# Tout ce qui précède le dernier segment numérique, qu'on complète à 3 chiffres
CODE_RE = re.compile(r'^([A-Z0-9-]+)-0*(\d+)$')

MOIS_FR = [
    'JANVIER', 'FÉVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN',
    'JUILLET', 'AOÛT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE',
]

# Seule la référence de l'arrêté est fixe : le n° du brevet est le code du certificat
DEFAULT_ARRETE = "ARRETE MINISTÉRIEL N°030/CABMIN/MIN-FPMA/JNP/RLK/SPDY/2020 DU 05 NOVEMBRE 2020"


def _prefix_candidates(name):
    """Préfixes possibles, du plus court au plus long, pour le nom d'une formation.

    Initiales des mots significatifs (2 premières lettres pour un mot seul), puis on
    approfondit avec les lettres suivantes du dernier mot : Transport -> TR, Travail -> TRA.
    """
    text = unicodedata.normalize('NFKD', name or '').encode('ascii', 'ignore').decode().upper()
    # Les mots d'une lettre sont ignorés : « Assistant(e) » -> ASSISTANT
    words = [w for w in re.split(r'[^A-Z0-9]+', text) if len(w) > 1 and w not in PREFIX_STOPWORDS]
    words = words[:PREFIX_MAX_WORDS] or ['FORMATION']
    head = ''.join(w[0] for w in words[:-1])
    last = words[-1]
    start = 1 if head else 2
    seen = []
    for depth in range(start, len(last) + 1):
        candidate = (head + last[:depth])[:10]
        if len(candidate) >= 2 and candidate not in seen:
            seen.append(candidate)
    return seen


class WebsiteTraining(models.Model):
    _inherit = 'website.training'

    certificate_title = fields.Char(
        string='Intitulé sur le certificat',
        help="Texte affiché après « a suivi la » sur le certificat. "
             "Ex : Formation d'Agent d'Accueil en Milieu Hospitalier")
    trainer_name = fields.Char(string='Formateur')
    director_name = fields.Char(string='Directeur Général')
    certificate_ids = fields.One2many('website.training.certificate', 'training_id', string='Certificats')
    certificate_count = fields.Integer(compute='_compute_certificate_count', string='Nombre de certificats')
    certificate_prefix = fields.Char(
        string='Préfixe des certificats', copy=False,
        help="Initiales de la formation utilisées pour numéroter les certificats (ex : FI → BSZ-2026-FI-001). "
             "Attribué automatiquement au premier certificat s'il est vide, puis figé.")
    certificate_sequence = fields.Integer(string='Dernier n° de certificat', default=0, copy=False, readonly=True)

    _sql_constraints = [
        ('certificate_prefix_unique', 'unique(certificate_prefix)',
         'Ce préfixe de certificat est déjà utilisé par une autre formation.'),
    ]

    @api.constrains('certificate_prefix')
    def _check_certificate_prefix(self):
        for rec in self:
            if rec.certificate_prefix and not PREFIX_RE.match(rec.certificate_prefix):
                raise ValidationError(_("Le préfixe doit contenir de 2 à 10 lettres majuscules ou chiffres."))

    def write(self, vals):
        if vals.get('certificate_prefix'):
            vals['certificate_prefix'] = vals['certificate_prefix'].strip().upper()
            if any(rec.certificate_ids and rec.certificate_prefix and rec.certificate_prefix != vals['certificate_prefix']
                   for rec in self):
                raise UserError(_("Le préfixe ne peut plus être modifié : des certificats ont déjà été numérotés."))
        return super().write(vals)

    def _get_certificate_prefix(self):
        self.ensure_one()
        if not self.certificate_prefix:
            taken = set(self.sudo().search([('certificate_prefix', '!=', False), ('id', '!=', self.id)])
                        .mapped('certificate_prefix'))
            candidates = _prefix_candidates(self.name)
            prefix = next((c for c in candidates if c not in taken), None)
            n = 2
            while not prefix:
                # Toutes les profondeurs sont prises : on suffixe par un chiffre
                prefix = next((c + str(n) for c in candidates if c + str(n) not in taken), None)
                n += 1
            self.sudo().certificate_prefix = prefix
        return self.certificate_prefix

    def _next_certificate_code(self, year):
        """Réserve le numéro suivant (verrou sur la formation : pas de doublon en concurrence).

        Format : BSZ-<année de délivrance>-<préfixe>-<n° d'ordre>, ex : BSZ-2026-FI-001.
        """
        self.ensure_one()
        prefix = self._get_certificate_prefix()
        self.env.cr.execute('SELECT certificate_sequence FROM website_training WHERE id = %s FOR UPDATE', [self.id])
        number = (self.env.cr.fetchone()[0] or 0) + 1
        self.env.cr.execute('UPDATE website_training SET certificate_sequence = %s WHERE id = %s', [number, self.id])
        self.invalidate_cache(['certificate_sequence'], self.ids)
        return '%s-%s-%s-%03d' % (CODE_PREFIX, year, prefix, number)

    @api.depends('certificate_ids')
    def _compute_certificate_count(self):
        for rec in self:
            rec.certificate_count = len(rec.certificate_ids)

    def action_open_certificate_wizard(self):
        self.ensure_one()
        return {
            'name': _('Enregistrer les participants certifiés'),
            'type': 'ir.actions.act_window',
            'res_model': 'website.training.certificate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_training_id': self.id},
        }

    def action_view_certificates(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('website_bensizwe.action_website_training_certificate')
        action['domain'] = [('training_id', '=', self.id)]
        action['context'] = {'default_training_id': self.id}
        return action

    def action_print_certificates(self):
        certificates = self.certificate_ids.filtered(lambda c: c.state == 'valid')
        if not certificates:
            raise UserError(_("Aucun certificat valide à imprimer pour cette formation."))
        # config=False : le certificat n'utilise pas la mise en page société, inutile d'ouvrir son assistant
        return self.env.ref('website_bensizwe.action_report_training_certificate').report_action(
            certificates, config=False)


class WebsiteTrainingCertificate(models.Model):
    _name = 'website.training.certificate'
    _description = 'Certificat de formation'
    _order = 'issue_date desc, id desc'
    _rec_name = 'code'

    # Numéro de série BSZ-<année>-<préfixe formation>-<n° d'ordre> (ex : BSZ-2026-FI-001), attribué à la création
    code = fields.Char(string='N° de série', readonly=True, copy=False, index=True)
    training_id = fields.Many2one('website.training', string='Formation', required=True, ondelete='restrict')
    candidat_id = fields.Many2one('website.user', string='Candidat',
                                  help="Laisser vide pour un participant non inscrit via le site.")
    participant_name = fields.Char(string='Nom du participant', required=True,
                                   help="Nom tel qu'il apparaîtra sur le certificat.")
    date_start = fields.Date(string='Début de la formation')
    date_end = fields.Date(string='Fin de la formation')
    issue_date = fields.Date(string="Date de délivrance", required=True, default=fields.Date.context_today)
    place = fields.Char(string='Lieu', default='Kinshasa')
    trainer_name = fields.Char(string='Formateur')
    director_name = fields.Char(string='Directeur Général')
    state = fields.Selection([
        ('valid', 'Valide'),
        ('revoked', 'Révoqué'),
    ], string='Statut', default='valid', required=True)
    verification_url = fields.Char(string='Lien de vérification', compute='_compute_verification_url')

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Le code de vérification doit être unique.'),
        ('training_candidat_unique', 'unique(training_id, candidat_id)',
         'Ce candidat possède déjà un certificat pour cette formation.'),
    ]

    @api.model
    def normalize_code(self, code):
        """' bsz 2026-fi-1 ' -> 'BSZ-2026-FI-001' : tolère la casse, les espaces et les zéros manquants."""
        code = re.sub(r'[\s_-]+', '-', (code or '').strip()).strip('-').upper()
        match = CODE_RE.match(code)
        return '%s-%03d' % (match.group(1), int(match.group(2))) if match else code

    @api.depends('code')
    def _compute_verification_url(self):
        for rec in self:
            rec.verification_url = '%s/certificat/verification/%s' % (rec.get_base_url(), rec.code)

    @api.onchange('candidat_id')
    def _onchange_candidat_id(self):
        if self.candidat_id:
            self.participant_name = self.candidat_id.name

    @api.onchange('training_id')
    def _onchange_training_id(self):
        training = self.training_id
        if training:
            self.date_start = training.date_start
            self.date_end = training.date_end
            self.trainer_name = training.trainer_name
            self.director_name = training.director_name

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            training = self.env['website.training'].browse(vals.get('training_id'))
            for field in ('date_start', 'date_end', 'trainer_name', 'director_name'):
                if not vals.get(field) and training:
                    vals[field] = training[field]
            if not vals.get('participant_name') and vals.get('candidat_id'):
                vals['participant_name'] = self.env['website.user'].browse(vals['candidat_id']).name
            if not vals.get('code') and training:
                issue_date = fields.Date.to_date(vals.get('issue_date')) or fields.Date.context_today(self)
                vals['code'] = training._next_certificate_code(issue_date.year)
        return super().create(vals_list)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError(_("La date de début doit précéder la date de fin."))

    def action_revoke(self):
        self.write({'state': 'revoked'})

    def action_validate(self):
        self.write({'state': 'valid'})

    # ===================================
    # HELPERS POUR LE RAPPORT / LA VÉRIFICATION
    # ===================================

    def get_training_label(self):
        self.ensure_one()
        return self.training_id.certificate_title or _('formation « %s »') % self.training_id.name

    def get_period_text(self):
        """Ex : 'du 17 au 31 AOÛT 2026', 'du 28 JUILLET au 03 AOÛT 2026', 'le 17 AOÛT 2026'."""
        self.ensure_one()
        start, end = self.date_start, self.date_end or self.date_start
        if not start:
            return ''

        def fmt(d, month=True, year=True):
            parts = ['%02d' % d.day]
            if month:
                parts.append(MOIS_FR[d.month - 1])
            if year:
                parts.append(str(d.year))
            return ' '.join(parts)

        if start == end:
            return _('le %s') % fmt(start)
        if start.year != end.year:
            return _('du %s au %s') % (fmt(start), fmt(end))
        if start.month != end.month:
            return _('du %s au %s') % (fmt(start, year=False), fmt(end))
        return _('du %s au %s') % (fmt(start, month=False, year=False), fmt(end))

    def get_brevet_text(self):
        self.ensure_one()
        arrete = self.env['ir.config_parameter'].sudo().get_param(
            'website_bensizwe.certificate_arrete', DEFAULT_ARRETE)
        return 'BREVET N° %s - %s' % (self.code, arrete)

    def get_qr_code_data_uri(self):
        self.ensure_one()
        png = self.env['ir.actions.report'].barcode(
            'QR', self.verification_url, width=300, height=300, quiet=0, barBorder=1, barLevel='M')
        return 'data:image/png;base64,%s' % base64.b64encode(png).decode()


class WebsiteTrainingCertificateWizard(models.TransientModel):
    _name = 'website.training.certificate.wizard'
    _description = 'Enregistrement des participants ayant complété la formation'

    training_id = fields.Many2one('website.training', string='Formation', required=True)
    candidat_ids = fields.Many2many(
        'website.user', string='Participants ayant complété la formation',
        domain="[('training_ids', 'in', training_id)]")
    issue_date = fields.Date(string='Date de délivrance', required=True, default=fields.Date.context_today)
    place = fields.Char(string='Lieu', default='Kinshasa', required=True)

    @api.onchange('training_id')
    def _onchange_training_id(self):
        # Pré-sélectionne les inscrits qui n'ont pas encore de certificat
        if self.training_id:
            already = self.training_id.certificate_ids.candidat_id
            registered = self.env['website.user'].search([('training_ids', 'in', self.training_id.id)])
            self.candidat_ids = registered - already

    def action_generate(self):
        self.ensure_one()
        if not self.candidat_ids:
            raise UserError(_("Veuillez sélectionner au moins un participant."))
        already = self.training_id.certificate_ids.candidat_id
        to_create = self.candidat_ids - already
        certificates = self.env['website.training.certificate'].create([{
            'training_id': self.training_id.id,
            'candidat_id': candidat.id,
            'participant_name': candidat.name,
            'issue_date': self.issue_date,
            'place': self.place,
        } for candidat in to_create])
        action = self.training_id.action_view_certificates()
        if certificates:
            action['domain'] = [('id', 'in', certificates.ids)]
        return action
