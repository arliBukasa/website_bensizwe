from odoo import models, fields, api

#inherit hr.department
class HrDepartment(models.Model):
    _inherit = 'hr.department'

class WebsiteRecruitment(models.Model):
    _inherit = 'hr.applicant'
    _description = 'Gestion des offres et candidats'

    
    candidat_id= fields.Many2one('website.user', string='Candidat')
    formation_ids = fields.One2many(
        'website.formation', 'candidat_id',
        string='Formations',
        compute='_compute_website_info',
        store=False,
        readonly=True
    )
    experience_ids = fields.One2many(
        'website.experience', 'candidat_id',
        string='Expériences',
        compute='_compute_website_info',
        store=False,
        readonly=True
    )
    education_ids = fields.One2many(
        'website.education', 'candidat_id',
        string='Éducation',
        compute='_compute_website_info',
        store=False,
        readonly=True
    )
    competence_ids = fields.One2many(
        'website.competence', 'candidat_id',
        string='Compétences',
        compute='_compute_website_info',
        store=False,
        readonly=True
    )
    training_ids = fields.One2many(
        'website.training', 'candidat_ids',
        string='Nos Formations suivies',
        compute='_compute_website_info',
        store=False,
        readonly=True
    )
    langage_ids = fields.One2many(
        'website.langage','candidat_ids',
        string='Langages',
        compute='_compute_website_info',
        store=False,
        readonly=True
    )

    def _compute_website_info(self):
        for rec in self:
            rec.formation_ids = rec.candidat_id.formation_ids
            rec.experience_ids = rec.candidat_id.experience_ids
            rec.education_ids = rec.candidat_id.education_ids
            rec.competence_ids = rec.candidat_id.competence_ids
            rec.training_ids = rec.candidat_id.training_ids
            rec.langage_ids = rec.candidat_id.langage_ids

class HrJob(models.Model):
    _inherit = 'hr.job'

    reference = fields.Char(string="Référence")
    department_id = fields.Many2one('hr.department', string="Département / Service")
    secteur = fields.Char(string="Secteur")
    localisation = fields.Char(string="Localisation")
    date_cloture = fields.Date(string="Date de Clôture")
    duree_contrat = fields.Selection([
        ('cdi', 'CDI'),
        ('cdd', 'CDD'),
        ('stage', 'Stage'),
        ('alternance', 'Alternance')
    ], string="Type de contrat", default='cdd')
    # Champs riches avec éditeur HTML
    contexte = fields.Html(string="Contexte")
    description_poste = fields.Html(string="Description du poste")  # déjà existant, mais redéfini ici si besoin
    qualification = fields.Html(string="Qualification")


class WebsiteTraining(models.Model):
    _name = 'website.training'
    _description = 'Gestion des formations'

    name = fields.Char(string='Nom de la formation')
    description = fields.Text(string='Description')
    date_start = fields.Date(string='Date de début')
    date_end = fields.Date(string='Date de fin')
    applicant_id = fields.Many2one('hr.applicant', string='Candidat')
    cout= fields.Float(string='Coût', default=0.0)
    header = fields.Binary(string='Entête de la formation')
    status = fields.Selection([
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé')
    ], string='Status', default='en_cours')
    candidat_ids = fields.One2many('website.user', 'training_ids', string='Candidats', store=True)

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.header:
            record._set_header_public()
        return record

    def write(self, vals):
        res = super().write(vals)
        if 'header' in vals:
            self._set_header_public()
        return res

    def _set_header_public(self):
        self.ensure_one()
        if self.header:
            self.env['ir.attachment'].sudo().search([
                ('res_model', '=', self._name),
                ('res_id', '=', self.id),
                ('res_field', '=', 'header')
            ]).write({'public': True})

class WebsiteUser(models.Model):
    _name = 'website.user'
    _description = 'Compte utilisateur'

    name = fields.Char(string='Nom')
    user_id = fields.Many2one(
        'res.users', 
        string='Utilisateur', 
        ondelete='cascade', 
        domain=lambda self: self._compute_user_domain()
    )
    email = fields.Char(string='Email')
    phone = fields.Char(string='Téléphone')
    etat_civil = fields.Selection([
    ('celibataire', 'Célibataire'),
    ('marie', 'Marié(e)'),
    ('divorce', 'Divorcé(e)'),
    ('veuf', 'Veuf/Veuve')
    ], string='État civil')

    date_naissance = fields.Date(string="Date de naissance")
    adresse = fields.Char(string="Adresse")
    nationalite = fields.Char(string="Nationalité")
    training_ids = fields.Many2many('website.training', string='Nos Formations suivies')
    experience_ids = fields.One2many('website.experience', 'candidat_id', string='Expériences')
    application_ids = fields.One2many('hr.applicant', 'candidat_id', string='Candidatures')
    formation_ids = fields.One2many('website.formation', 'candidat_id', string='Autres Formations')
    education_ids = fields.One2many('website.education', 'candidat_id', string='Education')
    competence_ids = fields.One2many('website.competence', 'candidat_id', string='Compétences')
    langage_ids = fields.Many2many('website.langage', string='Langages', relation='website_langage_candidat_rel')


    @api.model
    def _compute_user_domain(self):
        group_portal = self.env.ref('base.group_portal', raise_if_not_found=False)
        return [('groups_id', 'in', [group_portal.id])] if group_portal else []

    @api.model
    def create(self, vals):
        user = super(WebsiteUser, self).create(vals)
        # cree un utilisateur portal pour le candidat verifier si le candidat a deja un utilisateur
        if not user.user_id:
            #verifier qu'aucun utilisateur n'existe avec le meme email
            user_login = self.env['res.users'].search([('login', '=', user.email)], limit=1)
            if not user_login:
                user.user_id = self.env['res.users'].create({
                    'name': user.name,
                    'login': user.email,
                    'email': user.email,
                    'phone': user.phone,
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
                })
            else:
                # afficher un message d'erreur
                raise ValueError('Un utilisateur existe deja avec cet email')
        return user

class WebsiteEducation(models.Model):
    _name = 'website.education'
    _description = 'Education'

    name = fields.Char(string='Nom')
    date_start = fields.Date(string='Date de début')
    date_end = fields.Date(string='Date de fin')
    description = fields.Text(string='Description')
    institution = fields.Char(string="Institution")
    diplome = fields.Char(string="Diplôme obtenu")
    candidat_id = fields.Many2one('website.user', string='Candidat')



class WebsiteExperience(models.Model):
    _name = 'website.experience'
    _description = 'Expérience professionnelle'

    name = fields.Char(string='Nom')
    date_start = fields.Date(string='Date de début')
    date_end = fields.Date(string='Date de fin')
    description = fields.Text(string='Description')
    candidat_id = fields.Many2one('website.user', string='Candidat')


class WebsiteFormation(models.Model):
    _name = 'website.formation'
    _description = 'Formation'

    name = fields.Char(string='Nom')
    date_start = fields.Date(string='Date de début')
    date_end = fields.Date(string='Date de fin')
    description = fields.Text(string='Description')
    candidat_id = fields.Many2one('website.user', string='Candidat')
    document_obtenu = fields.Char(string="Document obtenu")

class WebsiteCompetence(models.Model):
    _name = 'website.competence'
    _description = 'Compétence'

    name = fields.Char(string='Nom')
    description = fields.Text(string='Description')
    candidat_id = fields.Many2one('website.user', string='Candidat')


class WebsiteLangage(models.Model):
    _name = 'website.langage'
    _description = 'Langage'

    name = fields.Char(string='Nom')
    description = fields.Text(string='Description')
    candidat_ids = fields.One2many('website.user', 'langage_ids', string='Candidats', store=True)