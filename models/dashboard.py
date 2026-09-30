from datetime import date

from odoo import models, fields, api, _


class WebsiteTrainingDashboard(models.TransientModel):
    """Tableau de bord des formations sur une période libre (formations dont le début tombe dans la période)."""
    _name = 'website.training.dashboard'
    _description = 'Tableau de bord des formations'

    date_from = fields.Date(string='Du', required=True, default=lambda self: date(fields.Date.context_today(self).year, 1, 1))
    date_to = fields.Date(string='Au', required=True, default=lambda self: date(fields.Date.context_today(self).year, 12, 31))
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    training_ids = fields.Many2many('website.training', compute='_compute_kpis', string='Formations de la période')
    training_count = fields.Integer(compute='_compute_kpis', string='Formations organisées')
    upcoming_count = fields.Integer(compute='_compute_kpis', string='À venir')
    ongoing_count = fields.Integer(compute='_compute_kpis', string='En cours')
    done_count = fields.Integer(compute='_compute_kpis', string='Terminées')
    cancelled_count = fields.Integer(compute='_compute_kpis', string='Annulées')

    registration_count = fields.Integer(compute='_compute_kpis', string='Candidats inscrits')
    online_count = fields.Integer(compute='_compute_kpis', string='Inscrits en ligne')
    fiche_count = fields.Integer(compute='_compute_kpis', string='Inscrits sur fiche')
    participant_count = fields.Integer(compute='_compute_kpis', string='Participants')
    pending_count = fields.Integer(compute='_compute_kpis', string='En attente de paiement')
    participation_rate = fields.Float(compute='_compute_kpis', string='Taux de participation global (%)')
    certified_count = fields.Integer(compute='_compute_kpis', string='Certificats délivrés')
    certification_rate = fields.Float(compute='_compute_kpis', string='Taux de certification (%)')
    amount_collected = fields.Monetary(compute='_compute_kpis', string='Montant encaissé')
    amount_remaining = fields.Monetary(compute='_compute_kpis', string='Reste à encaisser')

    def _period_domain(self, field='date_start'):
        return [(field, '>=', self.date_from), (field, '<=', self.date_to)]

    @api.depends('date_from', 'date_to')
    def _compute_kpis(self):
        Training = self.env['website.training']
        for rec in self:
            trainings = Training.search(rec._period_domain(), order='date_start') if rec.date_from and rec.date_to else Training
            states = trainings.mapped('period_state')
            regs = trainings.registration_ids
            participants = regs.filtered(lambda r: r.state == 'confirmed')
            active = regs.filtered(lambda r: r.state != 'cancelled')
            rec.training_ids = trainings
            rec.cancelled_count = states.count('cancelled')
            rec.training_count = len(trainings) - rec.cancelled_count
            rec.upcoming_count = states.count('upcoming')
            rec.ongoing_count = states.count('ongoing')
            rec.done_count = states.count('done')
            rec.registration_count = len(regs)
            rec.online_count = len(regs.filtered(lambda r: r.source == 'website'))
            rec.fiche_count = len(regs.filtered(lambda r: r.source == 'fiche'))
            rec.participant_count = len(participants)
            rec.pending_count = len(regs.filtered(lambda r: r.state == 'registered'))
            # Taux global pondéré : total participants / total candidats (et non moyenne des taux)
            rec.participation_rate = 100.0 * len(participants) / len(regs) if regs else 0.0
            rec.certified_count = sum(trainings.mapped('certified_count'))
            rec.certification_rate = 100.0 * rec.certified_count / len(participants) if participants else 0.0
            rec.amount_collected = sum(active.mapped('amount_paid'))
            rec.amount_remaining = sum(active.mapped('balance'))

    def _open(self, xmlid, domain, name, context=None):
        action = self.env['ir.actions.act_window']._for_xml_id(xmlid)
        action.update({'domain': domain, 'name': name, 'context': context or {}})
        return action

    def action_open_trainings(self):
        return self._open('website_bensizwe.action_website_training', self._period_domain(),
                          _('Formations du %s au %s') % (self.date_from.strftime('%d/%m/%Y'), self.date_to.strftime('%d/%m/%Y')))

    def action_open_registrations(self):
        return self._open('website_bensizwe.action_website_training_registration', self._period_domain(),
                          _('Candidats inscrits de la période'), {'search_default_group_training': 1})

    def action_open_participants(self):
        return self._open('website_bensizwe.action_website_training_registration',
                          self._period_domain() + [('state', '=', 'confirmed')],
                          _('Participants de la période'), {'search_default_group_training': 1})

    def action_open_pending(self):
        return self._open('website_bensizwe.action_website_training_registration',
                          self._period_domain() + [('state', '=', 'registered')],
                          _('Candidats en attente de paiement'), {'search_default_group_training': 1})

    def action_open_analysis(self):
        return self._open('website_bensizwe.action_website_training_registration_analysis', self._period_domain(),
                          _('Analyse des inscriptions'))
