# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db
from odoo.exceptions import UserError
import werkzeug
import logging
import re

_logger = logging.getLogger(__name__)


class FormationAuthController(http.Controller):
    """Contrôleur pour l'authentification lors de l'inscription aux formations"""

    @http.route('/formation/auth', type='http', auth='public', website=True, sitemap=False)
    def formation_auth(self, formation_id=None, redirect=None, **kwargs):
        """Page d'authentification unifiée pour les formations"""
        ensure_db()
        
        # Récupérer la formation si ID fourni
        formation = None
        if formation_id:
            try:
                formation = request.env['website.training'].sudo().browse(int(formation_id))
                if not formation.exists():
                    formation = None
            except (ValueError, TypeError):
                formation = None

        # Préparer les valeurs pour le template
        values = {
            'formation_id': formation_id,
            'formation': formation,
            'redirect': redirect or '/formations',
            'login_error': kwargs.get('login_error'),
            'signup_error': kwargs.get('signup_error'),
        }

        return request.render('website_bensizwe.formation_auth_unified_template', values)

    @http.route('/formation/auth/login', type='http', auth='public', website=True, sitemap=False, methods=['POST'])
    def formation_login(self, **kwargs):
        """Traiter la connexion lors de l'inscription à une formation"""
        ensure_db()
        
        email = kwargs.get('email', '').strip()
        password = kwargs.get('password', '')
        formation_id = kwargs.get('formation_id')
        redirect_url = kwargs.get('redirect', '/formations')

        if not email or not password:
            return self._redirect_with_error(
                '/formation/auth',
                'login_error',
                'Email et mot de passe requis',
                formation_id=formation_id,
                redirect=redirect_url
            )

        try:
            # Tentative de connexion
            request.session.authenticate(request.session.db, email, password)
            
            # Vérifier que l'utilisateur est bien un candidat
            user = request.env.user
            if not user.is_candidate:
                # Marquer comme candidat s'il ne l'est pas déjà
                user.sudo().write({'is_candidate': True})

            # Redirection après connexion réussie
            if formation_id:
                return request.redirect(f'/formation/{formation_id}/register')
            else:
                return request.redirect(redirect_url)

        except Exception as e:
            _logger.info("Formation login failed for email %s: %s", email, str(e))
            return self._redirect_with_error(
                '/formation/auth',
                'login_error',
                'Email ou mot de passe incorrect',
                formation_id=formation_id,
                redirect=redirect_url,
                email=email
            )

    @http.route('/formation/auth/signup', type='http', auth='public', website=True, sitemap=False, methods=['POST'])
    def formation_signup(self, **kwargs):
        """Traiter l'inscription complète lors de l'inscription à une formation"""
        ensure_db()
        
        formation_id = kwargs.get('formation_id')
        redirect_url = kwargs.get('redirect', '/formations')

        # Validation des champs requis
        required_fields = ['name', 'email', 'phone', 'password', 'password_confirm']
        missing_fields = [field for field in required_fields if not kwargs.get(field, '').strip()]
        
        if missing_fields:
            return self._redirect_with_error(
                '/formation/auth',
                'signup_error',
                f'Champs requis manquants: {", ".join(missing_fields)}',
                formation_id=formation_id,
                redirect=redirect_url,
                **kwargs
            )

        # Validation de l'email
        email = kwargs.get('email', '').strip().lower()
        if not self._validate_email(email):
            return self._redirect_with_error(
                '/formation/auth',
                'signup_error',
                'Format d\'email invalide',
                formation_id=formation_id,
                redirect=redirect_url,
                **kwargs
            )

        # Validation des mots de passe
        password = kwargs.get('password', '')
        password_confirm = kwargs.get('password_confirm', '')
        
        if password != password_confirm:
            return self._redirect_with_error(
                '/formation/auth',
                'signup_error',
                'Les mots de passe ne correspondent pas',
                formation_id=formation_id,
                redirect=redirect_url,
                **kwargs
            )

        if len(password) < 8:
            return self._redirect_with_error(
                '/formation/auth',
                'signup_error',
                'Le mot de passe doit contenir au moins 8 caractères',
                formation_id=formation_id,
                redirect=redirect_url,
                **kwargs
            )

        # Validation du téléphone
        phone = kwargs.get('phone', '').strip()
        if not self._validate_phone(phone):
            return self._redirect_with_error(
                '/formation/auth',
                'signup_error',
                'Format de téléphone invalide (ex: +223 XX XX XX XX)',
                formation_id=formation_id,
                redirect=redirect_url,
                **kwargs
            )

        # Vérification des conditions acceptées
        if not kwargs.get('accept_terms'):
            return self._redirect_with_error(
                '/formation/auth',
                'signup_error',
                'Vous devez accepter les conditions générales',
                formation_id=formation_id,
                redirect=redirect_url,
                **kwargs
            )

        try:
            # Vérifier si l'email existe déjà
            existing_user = request.env['res.users'].sudo().search([('email', '=', email)], limit=1)
            if existing_user:
                return self._redirect_with_error(
                    '/formation/auth',
                    'signup_error',
                    'Un compte avec cette adresse email existe déjà. Veuillez vous connecter.',
                    formation_id=formation_id,
                    redirect=redirect_url,
                    **kwargs
                )

            # Créer le nouvel utilisateur
            user_values = {
                'name': kwargs.get('name', '').strip(),
                'email': email,
                'login': email,
                'password': password,
                'is_candidate': True,
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                # Informations personnelles
                'phone': phone,
                'birth_date': kwargs.get('birth_date') or False,
                'gender': kwargs.get('gender') or False,
                'address': kwargs.get('address', '').strip() or False,
                # Informations professionnelles
                'current_job': kwargs.get('current_job', '').strip() or False,
                'company': kwargs.get('company', '').strip() or False,
                'experience_years': kwargs.get('experience_years') or False,
                'education_level': kwargs.get('education_level') or False,
                'specialization': kwargs.get('specialization', '').strip() or False,
                'linkedin_profile': kwargs.get('linkedin_profile', '').strip() or False,
                # Motivation et newsletter
                'motivation': kwargs.get('motivation', '').strip() or False,
                'newsletter_subscription': bool(kwargs.get('newsletter')),
            }

            new_user = request.env['res.users'].sudo().create(user_values)
            
            # Connecter automatiquement le nouvel utilisateur
            request.session.authenticate(request.session.db, email, password)

            # Créer une entrée dans hr.applicant si ce n'est pas déjà fait
            if not request.env['hr.applicant'].sudo().search([('email_from', '=', email)], limit=1):
                applicant_values = {
                    'name': new_user.name,
                    'email_from': email,
                    'partner_phone': phone,
                    'description': kwargs.get('motivation', ''),
                    'user_id': new_user.id,
                }
                request.env['hr.applicant'].sudo().create(applicant_values)

            # Log de l'inscription réussie
            _logger.info("New candidate registered successfully: %s (ID: %s)", email, new_user.id)

            # Redirection après inscription réussie
            if formation_id:
                return request.redirect(f'/formation/{formation_id}/register')
            else:
                return request.redirect(redirect_url)

        except SignupError as e:
            _logger.warning("Signup error for email %s: %s", email, str(e))
            return self._redirect_with_error(
                '/formation/auth',
                'signup_error',
                str(e),
                formation_id=formation_id,
                redirect=redirect_url,
                **kwargs
            )
        except Exception as e:
            _logger.error("Unexpected error during signup for email %s: %s", email, str(e))
            return self._redirect_with_error(
                '/formation/auth',
                'signup_error',
                'Une erreur s\'est produite lors de la création du compte. Veuillez réessayer.',
                formation_id=formation_id,
                redirect=redirect_url,
                **kwargs
            )

    def _redirect_with_error(self, url, error_type, message, **params):
        """Rediriger avec un message d'erreur"""
        params[error_type] = message
        query_string = werkzeug.urls.url_encode(params)
        return request.redirect(f"{url}?{query_string}")

    def _validate_email(self, email):
        """Valider le format de l'email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _validate_phone(self, phone):
        """Valider le format du téléphone malien"""
        if not phone:
            return False
        
        # Nettoyer le numéro
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Formats acceptés pour le Mali:
        # +223XXXXXXXX (8 chiffres après +223)
        # 223XXXXXXXX
        # XXXXXXXX (8 chiffres locaux)
        patterns = [
            r'^\+223\d{8}$',  # +223XXXXXXXX
            r'^223\d{8}$',    # 223XXXXXXXX
            r'^\d{8}$',       # XXXXXXXX (format local)
        ]
        
        return any(re.match(pattern, clean_phone) for pattern in patterns)

    @http.route('/formation/<int:formation_id>/register', type='http', auth='user', website=True)
    def formation_register(self, formation_id, **kwargs):
        """Page d'inscription définitive à une formation (après authentification)"""
        formation = request.env['website.training'].browse(formation_id)
        
        if not formation.exists():
            return request.not_found()

        # Vérifier si l'utilisateur est déjà inscrit
        existing_registration = request.env['website.training.registration'].search([
            ('training_id', '=', formation_id),
            ('user_id', '=', request.env.user.id),
        ], limit=1)

        if existing_registration:
            return request.render('website_bensizwe.formation_already_registered', {
                'formation': formation,
                'registration': existing_registration,
            })

        if request.httprequest.method == 'POST':
            # Créer l'inscription
            registration_values = {
                'training_id': formation_id,
                'user_id': request.env.user.id,
                'registration_date': fields.Date.today(),
                'state': 'registered',
            }
            
            registration = request.env['website.training.registration'].create(registration_values)
            
            return request.render('website_bensizwe.formation_registration_success', {
                'formation': formation,
                'registration': registration,
            })

        # Afficher la page de confirmation d'inscription
        return request.render('website_bensizwe.formation_registration_confirm', {
            'formation': formation,
            'user': request.env.user,
        })
