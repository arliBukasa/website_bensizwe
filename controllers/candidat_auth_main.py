# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging


class CandidatAuth(http.Controller):

    def _authenticate_user_by_id(self, user_id):
        """Authentifie un utilisateur par son ID (méthode programmatique)"""
        try:
            user = request.env['res.users'].sudo().browse(user_id)
            if user.exists():
                request.session.uid = user_id
                request.env.user = user
                logging.info("User authenticated programmatically: %s (ID: %s)", user.email, user_id)
                return True
            return False
        except Exception as e:
            logging.error("Error in programmatic authentication: %s", str(e))
            return False

    def _authenticate_user_by_token(self, token):
        """Authentifie un utilisateur via un token de session"""
        try:
            # Rechercher l'utilisateur par token (si vous stockez des tokens de session)
            user = request.env['res.users'].sudo().search([
                ('reset_password_token', '=', token)  # Exemple avec token de reset
            ], limit=1)
            
            if user:
                request.session.uid = user.id
                request.env.user = user
                logging.info("User authenticated by token: %s", user.email)
                return user
            return False
        except Exception as e:
            logging.error("Error in token authentication: %s", str(e))
            return False

    def _authenticate_user_object(self, user):
        """Authentifie un objet utilisateur directement"""
        try:
            if user and user.exists():
                request.session.uid = user.id
                request.env.user = user
                request.session.login = user.login
                # Mettre à jour la session avec les informations utilisateur
                request.session.session_token = request.session.sid
                logging.info("User object authenticated: %s (ID: %s)", user.email, user.id)
                return True
            return False
        except Exception as e:
            logging.error("Error authenticating user object: %s", str(e))
            return False

    @http.route('/candidat/login', type='http', auth='public', website=True)
    def candidat_login(self, **post):
        # Utiliser le nouveau template d'authentification unifié
        values = {
            'formation_id': None,
            'formation': None,
            'redirect': '/mon-espace',
            'login_error': None,
            'signup_error': None,
        }
        return request.render('website_bensizwe.formation_auth_unified_template', values)

    @http.route('/candidat/login/submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def candidat_login_submit(self, **post):
        email = post.get('login', '').strip()
        password = post.get('password', '')
        phone = post.get('phone', '').strip()

        logging.info("=================== Login attempt for email: %s , phone : %s,password: %s", email, phone, password)

        if not email or not password:
            values = {
                'formation_id': None,
                'formation': None,
                'redirect': '/mon-espace',
                'login_error': 'Email et mot de passe requis',
                'signup_error': None,
            }
            return request.render('website_bensizwe.formation_auth_unified_template', values)
        if not phone:
            values = {
                'formation_id': None,
                'formation': None,
                'redirect': '/mon-espace',
                'login_error': 'Le numéro de téléphone est requis',
                'signup_error': None,
            }
            return request.render('website_bensizwe.formation_auth_unified_template', values)

        try:
            # Tentative de connexion avec vérification du téléphone
            user = request.env['res.users'].sudo().search([
                ('login', '=', email),
                ('phone', '=', phone)  # Vérification supplémentaire du téléphone
            ], limit=1)
            
            if user:
                # Méthode 1: Authentification classique avec mot de passe
                request.session.authenticate(request.session.db, email, password)
                
                # Méthode 2: Authentification programmatique sans mot de passe (optionnelle)
                # request.session.uid = user.id
                # request.env.user = user
                
                logging.info("Authentication successful for user: %s (ID: %s)", user.email, user.id)
            else:
                raise Exception("Utilisateur non trouvé ou téléphone incorrect")
            
            # Vérifier que l'utilisateur est bien un candidat
            user = request.env.user
           
            #s'il n'a pas de téléphone, on le met à jour
            #if not user.phone:
            #    user.sudo().write({'phone': phone})

            # Redirection vers l'espace candidat
            return request.redirect('/mon-espace')

        except Exception as e:
            logging.info("Login failed for email %s: %s", email, str(e))
            values = {
                'formation_id': None,
                'formation': None,
                'redirect': '/mon-espace',
                'login_error': 'Email ou mot de passe incorrect',
                'signup_error': None,
            }
            return request.render('website_bensizwe.formation_auth_unified_template', values)

    @http.route('/candidat/signup/<int:id>', type='http', auth='public', website=True)
    def candidat_signup(self, id, **post):
        # Utiliser le nouveau template d'authentification unifié avec onglet inscription actif
        # get formation id
        formation_id = id
        logging.info("=================== Signup page for training ID: %s, post: %s", formation_id, post)
        formation = request.env['website.training'].sudo().browse(int(formation_id)) if formation_id else None
        logging.info("=================== Signup page for training ID: %s, formation: %s", formation_id, formation)
        values = {
            'formation_id': formation_id,
            'formation': formation,
            'redirect': '/mon-espace',
            'login_error': None,
            'signup_error':None,
            'show_signup': True,  # Pour activer l'onglet inscription par défaut
        }
        logging.info("=================== Signup page values: %s", values)
        return request.render('website_bensizwe.formation_auth_unified_template', values)

    @http.route('/candidat/signup/submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def candidat_signup_submit(self, **post):
        name = post.get('name', '').strip()
        email = post.get('email', '').strip().lower()
        password = post.get('password', '')

        # Validation des champs requis
        if not name or not email or not password:
            values = {
                'formation_id': None,
                'formation': None,
                'redirect': '/mon-espace',
                'login_error': None,
                'signup_error': 'Tous les champs sont requis',
                'show_signup': True,
            }
            return request.render('website_bensizwe.formation_auth_unified_template', values)

        # Vérifier si l'email existe déjà
        existing_user = request.env['res.users'].sudo().search([('email', '=', email)], limit=1)
        if existing_user:
            values = {
                'formation_id': None,
                'formation': None,
                'redirect': '/mon-espace',
                'login_error': None,
                'signup_error': 'Un compte avec cette adresse email existe déjà. Veuillez vous connecter.',
                'show_signup': True,
            }
            return request.render('website_bensizwe.formation_auth_unified_template', values)

        try:
            # Créer le nouvel utilisateur
            new_user = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'email': email,
                'password': password,
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])]
            })

            if new_user:
                # Créer l'entrée dans website.user si elle n'existe pas
                if not request.env['website.user'].sudo().search([('email', '=', email)], limit=1):
                    request.env['website.user'].sudo().create({
                        'name': name,
                        'email': email,
                        'user_id': new_user.id
                    })
                logging.info("New candidate registered successfully: %s (ID: %s)", email, new_user.id)

            # Connecter automatiquement le nouvel utilisateur
            request.session.authenticate(request.session.db, email, password)

            

            # Redirection vers l'espace candidat
            return request.redirect('/mon-espace')

        except Exception as e:
            logging.error("Unexpected error during signup for email %s: %s", email, str(e))
            values = {
                'formation_id': None,
                'formation': None,
                'redirect': '/mon-espace',
                'login_error': None,
                'signup_error': 'Une erreur s\'est produite lors de la création du compte. Veuillez réessayer.',
                'show_signup': True,
            }
            return request.render('website_bensizwe.formation_auth_unified_template', values)

    @http.route('/candidat/trainning/submit', type='http', auth='public', website=True)
    def candidat_trainning_submit(self, **post):
        formation_id = post.get('formation_id')
        name = post.get('name', '').strip()
        email = post.get('email', '').strip().lower()
        phone = post.get('phone', '').strip()
        redirect = post.get('redirect', '/mon-espace')

        logging.info("=================== Signup attempt for training ID: %s, email: %s , phone : %s", formation_id, email, phone)

        # Validation des champs requis
        if not name or not email or not phone:
            values = {
                'formation_id': formation_id,
                'formation': request.env['website.training'].sudo().browse(int(formation_id)) if formation_id else None,
                'redirect': redirect,
                'login_error': None,
                'signup_error': 'Tous les champs sont requis',
                'show_signup': True,
            }
            logging.info("=================== Signup missing fields values: %s", values)
            return request.render('website_bensizwe.formation_auth_unified_template', values)

        # Vérifier si l'email existe déjà
        existing_user = request.env['res.users'].sudo().search([('email', '=', email)], limit=1)
        
        try:
            if existing_user:
                user = existing_user
            else:
                # Créer le nouvel utilisateur
                user = request.env['res.users'].sudo().create({
                    'name': name,
                    'login': email,
                    'email': email,
                    'password': phone,  # Utiliser le téléphone comme mot de passe initial
                    'phone': phone,
                    'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])]
                })
                # Créer l'entrée dans website.user si elle n'existe pas
                if not request.env['website.user'].sudo().search([('email', '=', email)], limit=1):
                    created_user = request.env['website.user'].sudo().create({
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'user_id': user.id
                    })
                    logging.info("============Website user created: %s", created_user)
            
            new_user = user

            # s'il y a une formation envoyée lie le candidat à la formation
            if formation_id and user:
                formation = request.env['website.training'].sudo().browse(int(formation_id))
                if formation:
                    candidat = request.env['website.user'].sudo().search([('user_id', '=', user.id)], limit=1)
                    if candidat:
                        if formation not in candidat.training_ids:
                            candidat.write({'training_ids': [(4, formation.id)]})
                            logging.info("============ User %s (ID: %s) enrolled in training ID: %s", email, user.id, formation_id)
                        else:
                            logging.info("============ User %s (ID: %s) already enrolled in training ID: %s", email, user.id, formation_id)
                    else:
                        logging.warning("================== No website.user found for user %s (ID: %s)", email, user.id)
                else:
                    logging.warning(" =================    No training found with ID: %s", formation_id)
            
            # Connecter automatiquement le nouvel utilisateur crée
            

            logging.info("=============New candidate registered!: %s (ID: %s)", email, new_user.id)
            # Redirection vers l'espace candidat
            return request.redirect('/')
        except Exception as e:
            logging.error("============Unexpected error during signup for email %s: %s", email, str(e))
            values = {
                'formation_id': formation_id,
                'formation': request.env['website.training'].sudo().browse(int(formation_id)) if formation_id else None,
                'redirect': redirect,
                'login_error': None,
                'signup_error': 'Une erreur s\'est produite lors de la création du compte. Veuillez réessayer.',
                'show_signup': True,
            }
            return request.render('website_bensizwe.formation_auth_unified_template', values)

    @http.route('/candidat/reset_password', type='http', auth='public', website=True)
    def candidat_reset_password(self, **kw):
        """Page de réinitialisation de mot de passe"""
        return request.render('website_bensizwe.candidat_reset_password_template')

    @http.route('/candidat/reset_password/submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def candidat_reset_password_submit(self, **post):
        """Traitement de la demande de réinitialisation"""
        email = post.get('email', '').strip().lower()
        
        if not email:
            return request.render('website_bensizwe.candidat_reset_password_template', {
                'error': 'Veuillez saisir votre adresse email'
            })
        
        # Vérifier si l'utilisateur existe
        user = request.env['res.users'].sudo().search([('email', '=', email)], limit=1)
        logging.info("================= Password reset requested for user: %s", user)
        
        if user:
            try:
                # Générer le token et l'envoyer par email
                token = user._generate_reset_token(user)
                
                logging.info("Password reset requested for user: %s, token: %s", email, token)
                
                return request.render('website_bensizwe.candidat_reset_password_template', {
                    'success': True
                })
            except Exception as e:
                logging.error("Error during password reset for %s: %s", email, str(e))
                return request.render('website_bensizwe.candidat_reset_password_template', {
                    'error': 'Une erreur s\'est produite. Veuillez réessayer.'
                })
        else:
            # Pour des raisons de sécurité, on affiche toujours succès même si l'email n'existe pas
            return request.render('website_bensizwe.candidat_reset_password_template', {
                'error': " il n'existe pas de compte associé à cette adresse email"
            })

    @http.route('/candidat/reset_password/confirm', type='http', auth='public', website=True)
    def candidat_reset_password_confirm(self, token=None, **kw):
        """Page de confirmation de réinitialisation avec token"""
        if not token:
            return request.redirect('/candidat/reset_password')
        
        # Valider le token
        user = request.env['res.users']._validate_reset_token(token)
        
        if not user:
            return request.render('website_bensizwe.candidat_reset_password_template', {
                'error': 'Le lien de réinitialisation est invalide ou expiré.'
            })
        
        logging.info("Valid reset token accessed for user: %s", user.email)
        
        return request.render('website_bensizwe.candidat_reset_password_confirm_template', {
            'token': token,
            'user': user
        })

    @http.route('/candidat/reset_password/confirm/submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def candidat_reset_password_confirm_submit(self, **post):
        """Traitement du nouveau mot de passe"""
        token = post.get('token', '')
        password = post.get('password', '')
        password_confirm = post.get('password_confirm', '')
        
        logging.info("=================== Password reset confirmation attempt with token: %s , password : %s , confirm : %s", token, password, password_confirm) 
        if not token or not password or not password_confirm:
            return request.render('website_bensizwe.candidat_reset_password_confirm_template', {
                'token': token,
                'error': 'Tous les champs sont requis'
            })
        
        if password != password_confirm:
            return request.render('website_bensizwe.candidat_reset_password_confirm_template', {
                'token': token,
                'error': 'Les mots de passe ne correspondent pas'
            })
        
        if len(password) < 8:
            return request.render('website_bensizwe.candidat_reset_password_confirm_template', {
                'token': token,
                'error': 'Le mot de passe doit contenir au moins 8 caractères'
            })
        
        # Réinitialiser le mot de passe avec le token
        user = request.env['res.users']._reset_password_with_token(token, password)
        
        if user:
            logging.info("============ Password successfully reset for user: %s", user.email)
            
            # Authentifier automatiquement l'utilisateur après la réinitialisation
            try:
                # Méthode 1: Authentification programmatique directe
                self._authenticate_user_object(user)
                
                # Alternative - Méthode 2: Authentification classique avec nouveau mot de passe
                # request.session.authenticate(request.session.db, user.login, password)
                
                logging.info("User automatically authenticated after password reset")
                
                # Rediriger vers l'espace utilisateur au lieu de la page de succès
                return request.redirect('/mon-espace')
                
            except Exception as e:
                logging.error("Error authenticating user after password reset: %s", str(e))
                # En cas d'erreur d'authentification, afficher la page de succès normale
                return request.render('website_bensizwe.candidat_reset_password_success_template', {
                    'user': user,
                    'auto_login_failed': True
                })
        else:
            return request.render('website_bensizwe.candidat_reset_password_confirm_template', {
                'token': token,
                'error': 'Le lien de réinitialisation est invalide ou expiré'
            })
