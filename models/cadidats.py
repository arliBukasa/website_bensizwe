from odoo import models, fields, api
# import datetime
from datetime import timedelta
import base64
from odoo.exceptions import ValidationError

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
    publication_state= fields.Selection([('en_cours', 'En cours'),('urgent', 'Urgent'), ('cloture', 'Clôturé')], string='État de publication', default='en_cours',compute='_compute_publication_state', store=True)

    # actualisation de l'etat en fonction des date_cloture expire si date_cloture < today,ungent si la date de cloture est dans moins d'une semaine
    @api.model
    def _compute_publication_state(self):
        today = fields.Date.today()
        jobs = self.search([])
        for job in jobs:
            if job.date_cloture and job.date_cloture < today:
                job.publication_state = 'cloture'
            elif job.date_cloture and job.date_cloture <= today + timedelta(days=7):
                job.publication_state = 'urgent'
            else:
                job.publication_state = 'en_cours'

class WebsiteTraining(models.Model):
    _name = 'website.training'
    _description = 'Gestion des formations'

    name = fields.Char(string='Nom de la formation')
    description = fields.Html(string='Description')
    description_html = fields.Html(string='Description HTML')
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
    candidat_ids = fields.Many2many('website.user', compute='_compute_candidat_ids',string="Candidats inscrits",store=False)
    is_published = fields.Boolean(string='Publié', default=False)
    image = fields.Image(string="Image", max_width=1024, max_height=1024)
    video_url = fields.Char(string="URL de la vidéo de présentation")
    pourquoi_suivre = fields.Html(string="Pourquoi suivre cette formation ?")
    objectifs = fields.Html(string="Objectifs de la formation ?")

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
        # force tous les attaches a header avec _force_public_url()
        for record in self.env['ir.attachment'].search([]):
            record._set_header_public()

    def _set_header_public(self):
        for rec in self:
            attachment = self.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'website.training'),
                ('res_id', '=', rec.id),
                ('res_field', '=', 'header')
            ], limit=1)
            if attachment:
                attachment.write({'public': True})
                # Construction manuelle de l'URL
                attachment.url = f'/web/image/{attachment.res_model}/{attachment.res_id}/{attachment.res_field}'
    
    @api.depends('name')
    def _compute_candidat_ids(self):
        for record in self:
            record.candidat_ids = self.env['website.user'].search([
                ('training_ids', 'in', record.id)
            ])

class WebsiteUser(models.Model):
    _name = 'website.user'
    _description = 'Compte utilisateur'

    # ===================================
    # INFORMATIONS PERSONNELLES DE BASE
    # ===================================
    name = fields.Char(string='Nom complet', required=True)
    first_name = fields.Char(string='Prénom')
    last_name = fields.Char(string='Nom de famille')
    user_id = fields.Many2one(
        'res.users', 
        string='Utilisateur', 
        ondelete='cascade', 
        domain=lambda self: self._compute_user_domain()
    )
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Téléphone')
    
    # ===================================
    # PHOTO DE PROFIL
    # ===================================
    avatar = fields.Image(
        string='Photo de profil',
        max_width=1024,
        max_height=1024,
        help="Photo de profil de l'utilisateur"
    )
    avatar_url = fields.Char(
        string='URL de l\'avatar',
        compute='_compute_avatar_url',
        store=True
    )
    
    # ===================================
    # INFORMATIONS PERSONNELLES ÉTENDUES
    # ===================================
    birth_date = fields.Date(string="Date de naissance")
    # Champ de compatibilité pour l'ancien nom
    date_naissance = fields.Date(
        string="Date de naissance (legacy)",
        related='birth_date',
        store=True,
        help="Champ de compatibilité - utilisez birth_date à la place"
    )
    age = fields.Integer(string="Âge", compute='_compute_age', store=True)
    gender = fields.Selection([
        ('male', 'Homme'),
        ('female', 'Femme'),
        ('other', 'Autre')
    ], string='Genre')
    
    etat_civil = fields.Selection([
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce', 'Divorcé(e)'),
        ('veuf', 'Veuf/Veuve')
    ], string='État civil')
    
    nationalite = fields.Char(string="Nationalité")
    
    # ===================================
    # ADRESSE COMPLÈTE
    # ===================================
    street = fields.Char(string="Rue")
    street2 = fields.Char(string="Complément d'adresse")
    city = fields.Char(string="Ville")
    zip_code = fields.Char(string="Code postal")
    state = fields.Char(string="État/Province")
    country = fields.Char(string="Pays")
    adresse = fields.Char(
        string="Adresse complète",
        compute='_compute_full_address',
        store=True
    )
    
    # ===================================
    # INFORMATIONS PROFESSIONNELLES
    # ===================================
    current_position = fields.Char(string="Poste actuel")
    current_company = fields.Char(string="Entreprise actuelle")
    experience_years = fields.Selection([
        ('0-1', '0-1 an'),
        ('2-5', '2-5 ans'),
        ('6-10', '6-10 ans'),
        ('10+', 'Plus de 10 ans')
    ], string="Années d'expérience")
    
    salary_expectation = fields.Float(string="Prétentions salariales")
    availability = fields.Selection([
        ('immediate', 'Immédiate'),
        ('1_month', 'Dans 1 mois'),
        ('2_months', 'Dans 2 mois'),
        ('3_months', 'Dans 3 mois ou plus')
    ], string="Disponibilité")
    
    # ===================================
    # PRÉSENTATION ET BIO
    # ===================================
    bio = fields.Text(
        string="Présentation personnelle",
        help="Décrivez-vous en quelques mots, vos objectifs professionnels..."
    )
    objective = fields.Text(
        string="Objectif professionnel",
        help="Quel est votre objectif de carrière ?"
    )
    
    # ===================================
    # RÉSEAUX SOCIAUX ET LIENS
    # ===================================
    linkedin_url = fields.Char(string="LinkedIn")
    website_url = fields.Char(string="Site web personnel")
    portfolio_url = fields.Char(string="Portfolio")
    github_url = fields.Char(string="GitHub")
    
    # ===================================
    # PRÉFÉRENCES ET PARAMÈTRES
    # ===================================
    preferred_language = fields.Selection([
        ('fr', 'Français'),
        ('en', 'Anglais'),
        ('es', 'Espagnol'),
        ('de', 'Allemand')
    ], string="Langue préférée", default='fr')
    
    notification_email = fields.Boolean(
        string="Notifications par email",
        default=True,
        help="Recevoir les notifications par email"
    )
    
    newsletter = fields.Boolean(
        string="Newsletter",
        default=False,
        help="S'abonner à la newsletter"
    )
    
    # ===================================
    # STATUT ET MÉTADONNÉES
    # ===================================
    is_active = fields.Boolean(string="Actif", default=True)
    last_connection = fields.Datetime(string="Dernière connexion")
    profile_completion = fields.Float(
        string="Complétude du profil (%)",
        compute='_compute_profile_completion',
        store=True
    )
    
    # ===================================
    # RELATIONS EXISTANTES (INCHANGÉES)
    # ===================================
    training_ids = fields.Many2many('website.training', string='Nos Formations suivies')
    experience_ids = fields.One2many('website.experience', 'candidat_id', string='Expériences')
    application_ids = fields.One2many('hr.applicant', 'candidat_id', string='Candidatures')
    formation_ids = fields.One2many('website.formation', 'candidat_id', string='Autres Formations')
    education_ids = fields.One2many('website.education', 'candidat_id', string='Education')
    competence_ids = fields.One2many('website.competence', 'candidat_id', string='Compétences')
    langage_ids = fields.Many2many('website.langage', string='Langages', relation='website_langage_candidat_rel')

    # ===================================
    # MÉTHODES DE CALCUL
    # ===================================
    
    @api.depends('avatar')
    def _compute_avatar_url(self):
        for record in self:
            if record.avatar:
                # Utiliser l'URL standard d'Odoo pour les champs image avec timestamp pour éviter le cache
                record.avatar_url = f'/web/image/website.user/{record.id}/avatar?unique={record.write_date or record.create_date}'
            else:
                record.avatar_url = '/website_bensizwe/static/src/img/default-avatar.png'
    
    @api.depends('birth_date')
    def _compute_age(self):
        from datetime import date
        for record in self:
            if record.birth_date:
                today = date.today()
                record.age = today.year - record.birth_date.year - (
                    (today.month, today.day) < (record.birth_date.month, record.birth_date.day)
                )
            else:
                record.age = 0
    
    @api.depends('street', 'street2', 'city', 'zip_code', 'state', 'country')
    def _compute_full_address(self):
        for record in self:
            address_parts = []
            if record.street:
                address_parts.append(record.street)
            if record.street2:
                address_parts.append(record.street2)
            if record.zip_code and record.city:
                address_parts.append(f"{record.zip_code} {record.city}")
            elif record.city:
                address_parts.append(record.city)
            if record.state:
                address_parts.append(record.state)
            if record.country:
                address_parts.append(record.country)
            
            record.adresse = ', '.join(address_parts)
    
    @api.depends(
        'first_name', 'last_name', 'email', 'phone', 'birth_date', 
        'city', 'current_position', 'bio', 'avatar'
    )
    def _compute_profile_completion(self):
        for record in self:
            total_fields = 9  # Nombre de champs importants
            completed_fields = 0
            
            # Vérifier chaque champ important
            if record.first_name:
                completed_fields += 1
            if record.last_name:
                completed_fields += 1
            if record.email:
                completed_fields += 1
            if record.phone:
                completed_fields += 1
            if record.birth_date:
                completed_fields += 1
            if record.city:
                completed_fields += 1
            if record.current_position:
                completed_fields += 1
            if record.bio:
                completed_fields += 1
            if record.avatar:
                completed_fields += 1
            
            record.profile_completion = (completed_fields / total_fields) * 100
    
    # ===================================
    # CONTRAINTES ET VALIDATIONS
    # ===================================
    
    @api.constrains('email')
    def _check_email_unique(self):
        for record in self:
            if record.email:
                existing = self.search([
                    ('email', '=', record.email),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError("Cette adresse email est déjà utilisée par un autre utilisateur.")
    
    @api.constrains('birth_date')
    def _check_birth_date(self):
        from datetime import date
        for record in self:
            if record.birth_date and record.birth_date > date.today():
                raise ValidationError("La date de naissance ne peut pas être dans le futur.")
    
    @api.constrains('phone')
    def _check_phone_format(self):
        import re
        for record in self:
            if record.phone:
                # Validation basique du format téléphone
                phone_pattern = r'^[\+]?[0-9\s\-\(\)]{10,}$'
                if not re.match(phone_pattern, record.phone):
                    raise ValidationError("Le format du numéro de téléphone n'est pas valide.")
    
    # ===================================
    # MÉTHODES DE DOMAINE ET CRÉATION
    # ===================================

    @api.model
    def _compute_user_domain(self):
        group_portal = self.env.ref('base.group_portal', raise_if_not_found=False)
        return [('groups_id', 'in', [group_portal.id])] if group_portal else []

    @api.model
    def create(self, vals):
        # Auto-complétion du nom complet
        if vals.get('first_name') and vals.get('last_name'):
            vals['name'] = f"{vals['first_name']} {vals['last_name']}"
        
        # Support de l'ancien champ date_naissance
        if vals.get('date_naissance') and not vals.get('birth_date'):
            vals['birth_date'] = vals['date_naissance']
        
        user = super(WebsiteUser, self).create(vals)
        
        # Créer un utilisateur portal pour le candidat
        if not user.user_id:
            # Vérifier qu'aucun utilisateur n'existe avec le même email
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
                raise ValidationError('Un utilisateur existe déjà avec cet email')
        
        return user
    
    def write(self, vals):
        # Auto-complétion du nom complet lors de la modification
        if 'first_name' in vals or 'last_name' in vals:
            first_name = vals.get('first_name', self.first_name)
            last_name = vals.get('last_name', self.last_name)
            if first_name and last_name:
                vals['name'] = f"{first_name} {last_name}"
        
        # Support de l'ancien champ date_naissance
        if 'date_naissance' in vals and 'birth_date' not in vals:
            vals['birth_date'] = vals['date_naissance']
        
        return super(WebsiteUser, self).write(vals)
    
    # ===================================
    # MÉTHODES UTILITAIRES
    # ===================================
    
    def get_full_name(self):
        """Retourne le nom complet formaté"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.name or "Utilisateur"
    
    def get_avatar_url(self):
        """Retourne l'URL de l'avatar ou une image par défaut"""
        if self.avatar:
            return f'/web/image/website.user/{self.id}/avatar'
        return '/website_bensizwe/static/src/img/default-avatar.png'
    
    def update_last_connection(self):
        """Met à jour la date de dernière connexion"""
        self.write({'last_connection': fields.Datetime.now()})
    
    def get_application_stats(self):
        """Retourne les statistiques des candidatures"""
        stats = {
            'total': len(self.application_ids),
            'pending': len(self.application_ids.filtered(lambda x: x.stage_id.name in ['Nouveau', 'En cours'])),
            'accepted': len(self.application_ids.filtered(lambda x: x.stage_id.name in ['Accepté', 'Embauché'])),
            'rejected': len(self.application_ids.filtered(lambda x: x.stage_id.name in ['Refusé', 'Rejeté']))
        }
        return stats

# ===================================
# MODÈLES EXISTANTS (INCHANGÉS)
# ===================================

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