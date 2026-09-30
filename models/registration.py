from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


def _current_source():
    """Inscription faite depuis le site (routes website) ou saisie au bureau (backend)."""
    try:
        return 'website' if request and getattr(request, 'is_frontend', False) else 'fiche'
    except RuntimeError:  # hors requête HTTP (cron, shell)
        return 'fiche'


class WebsiteTrainingRegistration(models.Model):
    """Inscription d'un candidat à une formation.

    Un candidat inscrit (en ligne ou sur fiche) ne devient participant qu'une fois
    le paiement soldé (ou exonéré) ; seuls les participants peuvent être certifiés.
    """
    _name = 'website.training.registration'
    _description = 'Inscription à une formation'
    _inherit = ['mail.thread']
    _order = 'registration_date desc, id desc'

    # Valeurs d'état reprises des templates portail existants (registered / confirmed / cancelled)
    STATES = [
        ('registered', 'Candidat inscrit'),
        ('confirmed', 'Participant'),
        ('cancelled', 'Annulé'),
    ]

    name = fields.Char(compute='_compute_name', store=True)
    training_id = fields.Many2one('website.training', string='Formation', required=True,
                                  ondelete='restrict', index=True, tracking=True)
    candidat_id = fields.Many2one('website.user', string='Candidat', required=True,
                                  ondelete='restrict', index=True, tracking=True)
    user_id = fields.Many2one('res.users', related='candidat_id.user_id', store=True, string='Utilisateur')
    email = fields.Char(related='candidat_id.email')
    phone = fields.Char(related='candidat_id.phone')
    registration_date = fields.Date(string="Date d'inscription", required=True, default=fields.Date.context_today)
    source = fields.Selection([
        ('website', 'En ligne'),
        ('fiche', 'Fiche (bureau)'),
    ], string='Source', required=True, default=lambda self: _current_source())
    state = fields.Selection(STATES, string='Statut', required=True, default='registered', tracking=True)

    # Période de la formation, stockée pour grouper / filtrer les analyses
    date_start = fields.Date(related='training_id.date_start', store=True, string='Début formation')
    date_end = fields.Date(related='training_id.date_end', store=True, string='Fin formation')

    # Paiement
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount_due = fields.Monetary(string='Montant dû', tracking=True)
    amount_paid = fields.Monetary(string='Montant payé', tracking=True)
    balance = fields.Monetary(string='Reste à payer', compute='_compute_payment', store=True)
    payment_date = fields.Date(string='Date de paiement')
    payment_method = fields.Selection([
        ('cash', 'Espèces'),
        ('mobile', 'Mobile money'),
        ('bank', 'Virement / dépôt bancaire'),
        ('other', 'Autre'),
    ], string='Mode de paiement')
    payment_ref = fields.Char(string='Référence paiement')
    is_exempt = fields.Boolean(string='Exonéré', tracking=True,
                               help="Participant dispensé de paiement (bourse, invité, partenaire...).")
    payment_state = fields.Selection([
        ('unpaid', 'Non payé'),
        ('partial', 'Partiel'),
        ('paid', 'Payé'),
        ('exempt', 'Exonéré'),
    ], string='Paiement', compute='_compute_payment', store=True)

    # Indicateurs agrégeables (moyenne = taux) pour les tableaux croisés
    is_participant = fields.Boolean(compute='_compute_participation', store=True, string='Participant ?')
    participation_rate = fields.Float(compute='_compute_participation', store=True, group_operator='avg',
                                      string='Taux de participation (%)')

    certificate_ids = fields.One2many('website.training.certificate', 'registration_id', string='Certificats')
    certificate_code = fields.Char(compute='_compute_certificate', string='N° certificat')
    note = fields.Text(string='Note')

    _sql_constraints = [
        ('training_candidat_unique', 'unique(training_id, candidat_id)',
         'Ce candidat est déjà inscrit à cette formation.'),
        ('amounts_positive', 'CHECK(amount_due >= 0 AND amount_paid >= 0)',
         'Les montants ne peuvent pas être négatifs.'),
    ]

    @api.depends('candidat_id.name', 'training_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = '%s - %s' % (rec.candidat_id.name or '', rec.training_id.name or '')

    @api.depends('amount_due', 'amount_paid', 'is_exempt')
    def _compute_payment(self):
        for rec in self:
            rec.balance = 0.0 if rec.is_exempt else max(rec.amount_due - rec.amount_paid, 0.0)
            if rec.is_exempt:
                rec.payment_state = 'exempt'
            elif rec.amount_paid and rec.amount_paid >= rec.amount_due:
                rec.payment_state = 'paid'
            elif rec.amount_paid:
                rec.payment_state = 'partial'
            else:
                rec.payment_state = 'paid' if not rec.amount_due else 'unpaid'

    @api.depends('state')
    def _compute_participation(self):
        for rec in self:
            rec.is_participant = rec.state == 'confirmed'
            rec.participation_rate = 100.0 if rec.is_participant else 0.0

    def _compute_certificate(self):
        for rec in self:
            rec.certificate_code = rec.certificate_ids[:1].code

    @api.onchange('training_id')
    def _onchange_training_id(self):
        if self.training_id and not self.amount_due:
            self.amount_due = self.training_id.cout

    @api.onchange('amount_paid')
    def _onchange_amount_paid(self):
        if self.amount_paid and not self.payment_date:
            self.payment_date = fields.Date.context_today(self)

    @api.model
    def _candidat_from_user(self, user):
        """Retrouve (ou crée) la fiche candidat d'un utilisateur du portail."""
        WebsiteUser = self.env['website.user'].sudo()
        candidat = WebsiteUser.search([('user_id', '=', user.id)], limit=1)
        if not candidat:
            candidat = WebsiteUser.search([('email', '=ilike', user.email or user.login)], limit=1)
        if not candidat:
            candidat = WebsiteUser.create({
                'name': user.name, 'email': user.email or user.login, 'phone': user.phone, 'user_id': user.id,
            })
        return candidat

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Compatibilité : les routes portail créent l'inscription avec user_id (res.users)
            user_id = vals.pop('user_id', None)
            if not vals.get('candidat_id') and user_id:
                vals['candidat_id'] = self._candidat_from_user(self.env['res.users'].browse(user_id)).id
            if 'amount_due' not in vals and vals.get('training_id'):
                vals['amount_due'] = self.env['website.training'].browse(vals['training_id']).cout
        records = super().create(vals_list)
        if not self.env.context.get('skip_training_sync'):
            for rec in records.sudo():
                if rec.training_id not in rec.candidat_id.training_ids:
                    rec.candidat_id.with_context(skip_training_sync=True).write(
                        {'training_ids': [(4, rec.training_id.id)]})
        return records

    @api.constrains('state', 'certificate_ids')
    def _check_certified_participant(self):
        for rec in self:
            if rec.certificate_ids and rec.state != 'confirmed':
                raise ValidationError(_(
                    "%s possède un certificat pour cette formation : l'inscription doit rester au statut "
                    "Participant (révoquez d'abord le certificat puis supprimez-le si nécessaire).") % rec.candidat_id.name)

    def action_confirm(self):
        """Candidat inscrit -> participant : exige un paiement soldé ou une exonération."""
        for rec in self:
            if rec.state == 'cancelled':
                raise UserError(_("L'inscription de %s est annulée.") % rec.candidat_id.name)
            if rec.payment_state not in ('paid', 'exempt'):
                raise UserError(_(
                    "%s ne peut pas être enregistré comme participant : paiement %s (reste %.2f %s). "
                    "Enregistrez le paiement ou cochez « Exonéré ».")
                    % (rec.candidat_id.name, dict(rec._fields['payment_state'].selection)[rec.payment_state].lower(),
                       rec.balance, rec.currency_id.symbol or ''))
        for training in self.training_id:
            confirming = len(self.filtered(lambda r: r.training_id == training and r.state != 'confirmed'))
            if training.max_participants and training.participant_count + confirming > training.max_participants:
                raise UserError(_("La formation « %s » est complète (%s participants maximum).")
                                % (training.name, training.max_participants))
        self.write({'state': 'confirmed'})

    def action_mark_paid(self):
        """Paiement intégral en un clic, puis passage en participant."""
        for rec in self.filtered(lambda r: r.state != 'cancelled'):
            rec.write({
                'amount_paid': rec.amount_due,
                'payment_date': rec.payment_date or fields.Date.context_today(rec),
            })
        self.filtered(lambda r: r.state == 'registered').action_confirm()

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset(self):
        self.write({'state': 'registered'})


class WebsiteUserRegistration(models.Model):
    _inherit = 'website.user'

    registration_ids = fields.One2many('website.training.registration', 'candidat_id', string='Inscriptions')

    def _sync_training_registrations(self):
        """Les flux du site ajoutent la formation dans training_ids : on crée l'inscription correspondante."""
        Registration = self.env['website.training.registration'].sudo().with_context(skip_training_sync=True)
        for candidat in self.sudo():
            missing = candidat.training_ids - candidat.registration_ids.training_id
            if missing:
                Registration.create([{'training_id': t.id, 'candidat_id': candidat.id} for t in missing])

    @api.model
    def create(self, vals):
        # Même signature (mono-enregistrement) que WebsiteUser.create dans cadidats.py
        record = super().create(vals)
        record.user_id.sudo().write({'is_candidate': True})
        if not self.env.context.get('skip_training_sync'):
            record._sync_training_registrations()
        return record

    def write(self, vals):
        res = super().write(vals)
        if vals.get('user_id'):
            self.user_id.sudo().write({'is_candidate': True})
        if 'training_ids' in vals and not self.env.context.get('skip_training_sync'):
            self._sync_training_registrations()
        return res


class ResUsersCandidate(models.Model):
    _inherit = 'res.users'

    # Utilisé par le portail (/my/formations) et la connexion formation
    is_candidate = fields.Boolean(string='Candidat', default=False)


class WebsiteTrainingParticipants(models.Model):
    _inherit = 'website.training'

    registration_ids = fields.One2many('website.training.registration', 'training_id', string='Inscriptions')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # Statistiques stockées : utilisables dans les listes, tableaux croisés et graphiques
    registration_count = fields.Integer(compute='_compute_participant_stats', store=True, string='Candidats inscrits')
    participant_count = fields.Integer(compute='_compute_participant_stats', store=True, string='Participants')
    participation_rate = fields.Float(compute='_compute_participant_stats', store=True, group_operator='avg',
                                      string='Taux de participation (%)')
    amount_collected = fields.Monetary(compute='_compute_participant_stats', store=True, string='Montant encaissé')
    amount_remaining = fields.Monetary(compute='_compute_participant_stats', store=True, string='Reste à encaisser')
    certified_count = fields.Integer(compute='_compute_participant_stats', store=True, string='Certifiés')

    # Alias lus par les templates du portail (portal_formations.xml, formation_registration_templates.xml)
    start_date = fields.Date(related='date_start', string='Début')
    price = fields.Float(related='cout', string='Prix')
    duration = fields.Char(compute='_compute_duration', string='Durée')
    max_participants = fields.Integer(string='Capacité', help="Nombre maximum de participants (0 = illimité).")
    available_spots = fields.Integer(compute='_compute_available_spots', string='Places restantes')

    period_state = fields.Selection([
        ('undated', 'Non planifiée'),
        ('upcoming', 'À venir'),
        ('ongoing', 'En cours'),
        ('done', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], compute='_compute_period_state', string='Suivi')

    @api.depends('registration_ids.state', 'registration_ids.amount_paid', 'registration_ids.balance',
                 'certificate_ids.state')
    def _compute_participant_stats(self):
        for rec in self:
            regs = rec.registration_ids
            active = regs.filtered(lambda r: r.state != 'cancelled')
            participants = regs.filtered(lambda r: r.state == 'confirmed')
            rec.registration_count = len(regs)
            rec.participant_count = len(participants)
            # Taux = participants / candidats inscrits (les annulations comptent comme non-participation)
            rec.participation_rate = 100.0 * len(participants) / len(regs) if regs else 0.0
            rec.amount_collected = sum(active.mapped('amount_paid'))
            rec.amount_remaining = sum(active.mapped('balance'))
            rec.certified_count = len(rec.certificate_ids.filtered(lambda c: c.state == 'valid'))

    @api.depends('max_participants', 'participant_count')
    def _compute_available_spots(self):
        for rec in self:
            rec.available_spots = max(rec.max_participants - rec.participant_count, 0) if rec.max_participants else 0

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for rec in self:
            days = (rec.date_end - rec.date_start).days + 1 if rec.date_start and rec.date_end else 0
            rec.duration = _('%s jour(s)') % days if days > 0 else False

    @api.depends('status', 'date_start', 'date_end')
    def _compute_period_state(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.status == 'annule':
                rec.period_state = 'cancelled'
            elif not rec.date_start:
                rec.period_state = 'undated'
            elif rec.date_start > today:
                rec.period_state = 'upcoming'
            elif (rec.date_end or rec.date_start) < today:
                rec.period_state = 'done'
            else:
                rec.period_state = 'ongoing'

    def action_view_registrations(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('website_bensizwe.action_website_training_registration')
        action['domain'] = [('training_id', '=', self.id)]
        action['context'] = {'default_training_id': self.id, 'search_default_group_state': 1}
        return action

    def action_print_participants(self):
        return self.env.ref('website_bensizwe.action_report_training_participants').report_action(self, config=False)
