# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
import base64
import json
from datetime import datetime, date
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class CandidatEspace(http.Controller):

    @http.route('/mon-espace', type='http', auth='public', website=True)
    def espace_candidat(self, **kwargs):
        """Page principale de l'espace candidat moderne"""
        if request.env.user._is_public():
            return request.redirect('/candidat/login')

        candidat = request.env['website.user'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not candidat:
            return request.redirect('/candidat/signup')

        # Mise à jour de la dernière connexion
        candidat.update_last_connection()

        # Offres recommandées (non encore postulées)
        postes_postules_ids = candidat.application_ids.mapped('job_id').ids
        offres = request.env['hr.job'].sudo().search([
            ('id', 'not in', postes_postules_ids),
            ('publication_state', '!=', 'cloture')
        ], limit=8)

        # Statistiques pour le dashboard
        stats = candidat.get_application_stats()

        return request.render('website_bensizwe.candidat_espace_template', {
            'candidat': candidat,
            'offres': offres,
            'stats': stats,
            'page_title': f"Espace de {candidat.get_full_name()}"
        })

    @http.route('/mon-espace/update', type='http', auth='user', methods=['POST'], csrf=True, website=True)
    def candidat_update_profile(self, **post):
        """Mise à jour complète du profil utilisateur"""
        try:
            candidat = request.env['website.user'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not candidat:
                return request.redirect('/candidat/signup')

            # Préparer les données de mise à jour
            update_data = {}
            
            # Informations personnelles
            if post.get('first_name'):
                update_data['first_name'] = post.get('first_name').strip()
            if post.get('last_name'):
                update_data['last_name'] = post.get('last_name').strip()
            if post.get('email'):
                update_data['email'] = post.get('email').strip()
            if post.get('phone'):
                update_data['phone'] = post.get('phone').strip()
            if post.get('birth_date'):
                try:
                    update_data['birth_date'] = datetime.strptime(post.get('birth_date'), '%Y-%m-%d').date()
                except ValueError:
                    pass
            if post.get('gender'):
                update_data['gender'] = post.get('gender')

            # Adresse
            if post.get('street'):
                update_data['street'] = post.get('street').strip()
            if post.get('city'):
                update_data['city'] = post.get('city').strip()
            if post.get('zip_code'):
                update_data['zip_code'] = post.get('zip_code').strip()
            if post.get('country'):
                update_data['country'] = post.get('country').strip()

            # Informations professionnelles
            if post.get('current_position'):
                update_data['current_position'] = post.get('current_position').strip()
            if post.get('experience_years'):
                update_data['experience_years'] = post.get('experience_years')
            if post.get('bio'):
                update_data['bio'] = post.get('bio').strip()
            if post.get('objective'):
                update_data['objective'] = post.get('objective').strip()

            # Réseaux sociaux
            if post.get('linkedin_url'):
                update_data['linkedin_url'] = post.get('linkedin_url').strip()
            if post.get('portfolio_url'):
                update_data['portfolio_url'] = post.get('portfolio_url').strip()

            # Préférences
            if post.get('notification_email'):
                update_data['notification_email'] = post.get('notification_email') == 'on'
            if post.get('newsletter'):
                update_data['newsletter'] = post.get('newsletter') == 'on'

            # Anciens champs pour compatibilité
            if post.get('nationalite'):
                update_data['nationalite'] = post.get('nationalite').strip()
            if post.get('etat_civil'):
                update_data['etat_civil'] = post.get('etat_civil')

            # Mettre à jour le candidat
            candidat.write(update_data)
            
            # Message de succès
            return request.redirect('/mon-espace?message=profile_updated')
            
        except ValidationError as e:
            _logger.error(f"Erreur de validation lors de la mise à jour du profil: {e}")
            return request.redirect('/mon-espace?error=validation_error')
        except Exception as e:
            _logger.error(f"Erreur lors de la mise à jour du profil: {e}")
            return request.redirect('/mon-espace?error=update_failed')

    @http.route('/mon-espace/upload-avatar', type='http', auth='user', methods=['POST'], csrf=True, website=True)
    def upload_avatar(self, **post):
        """Upload de la photo de profil"""
        try:
            candidat = request.env['website.user'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not candidat:
                return json.dumps({'error': 'Candidat non trouvé'})

            avatar_file = post.get('avatar')
            if avatar_file:
                # Vérifier la taille du fichier (max 5MB)
                if len(avatar_file.read()) > 5 * 1024 * 1024:
                    return json.dumps({'error': 'Le fichier est trop volumineux (max 5MB)'})
                
                avatar_file.seek(0)  # Reset file pointer
                
                # Vérifier le type de fichier
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if avatar_file.content_type not in allowed_types:
                    return json.dumps({'error': 'Type de fichier non autorisé'})
                
                # Encoder en base64
                avatar_data = base64.b64encode(avatar_file.read())
                
                # Mettre à jour l'avatar
                candidat.write({'avatar': avatar_data})
                
                return json.dumps({
                    'success': True,
                    'avatar_url': candidat.get_avatar_url()
                })
            else:
                return json.dumps({'error': 'Aucun fichier sélectionné'})
                
        except Exception as e:
            _logger.error(f"Erreur lors de l'upload de l'avatar: {e}")
            return json.dumps({'error': 'Erreur lors de l\'upload'})

    @http.route('/mon-espace/modifier', type='http', auth='user', website=True)
    def candidat_modifier(self, **kwargs):
        """Page de modification du profil (conservée pour compatibilité)"""
        candidat = request.env['website.user'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not candidat:
            return request.redirect('/candidat/signup')
            
        return request.render('website_bensizwe.candidat_update_template', {
            'candidat': candidat
        })

    @http.route('/mon-espace/actualiser', type='http', auth='user', methods=['POST'], csrf=True, website=True)
    def candidat_modifier_post(self, **post):
        """Ancienne méthode de mise à jour (conservée pour compatibilité)"""
        try:
            candidat = request.env['website.user'].sudo().browse(int(post.get('candidat_id')))
            if candidat:
                candidat.write({
                    'name': post.get('name'),
                    'email': post.get('email'),
                    'phone': post.get('phone'),
                    'nationalite': post.get('nationalite'),
                    'adresse': post.get('adresse'),
                    'date_naissance': post.get('date_naissance'),
                    'etat_civil': post.get('etat_civil'),
                })
            return request.redirect('/mon-espace')
        except Exception as e:
            _logger.error(f"Erreur lors de la mise à jour du profil (méthode legacy): {e}")
            return request.redirect('/mon-espace?error=update_failed')

    @http.route('/mon-espace/imprimer-cv', type='http', auth='user', website=True)
    def imprimer_cv(self, **kwargs):
        """Génération et téléchargement du CV en PDF"""
        candidat = request.env['website.user'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not candidat:
            return request.redirect('/mon-espace')

        report_ref = 'website_bensizwe.report_cv_pdf'
        return request.redirect(f'/report/pdf/{report_ref}/{candidat.id}')

    @http.route('/mon-espace/applications', type='http', auth='user', website=True)
    def candidat_applications(self, **kwargs):
        """Page détaillée des candidatures"""
        candidat = request.env['website.user'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not candidat:
            return request.redirect('/candidat/signup')

        # Récupérer toutes les candidatures avec détails
        applications = candidat.application_ids.sorted('create_date', reverse=True)
        
        return request.render('website_bensizwe.candidat_applications_template', {
            'candidat': candidat,
            'applications': applications,
            'page_title': 'Mes candidatures'
        })

    @http.route('/mon-espace/formations', type='http', auth='user', website=True)
    def candidat_formations(self, **kwargs):
        """Page détaillée des formations"""
        candidat = request.env['website.user'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not candidat:
            return request.redirect('/candidat/signup')

        # Formations disponibles
        formations_disponibles = request.env['website.training'].sudo().search([
            ('is_published', '=', True),
            ('status', '=', 'en_cours')
        ])
        
        return request.render('website_bensizwe.candidat_formations_template', {
            'candidat': candidat,
            'formations_disponibles': formations_disponibles,
            'page_title': 'Mes formations'
        })

    @http.route('/mon-espace/settings', type='http', auth='user', website=True)
    def candidat_settings(self, **kwargs):
        """Page des paramètres du compte"""
        candidat = request.env['website.user'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not candidat:
            return request.redirect('/candidat/signup')
            
        return request.render('website_bensizwe.candidat_settings_template', {
            'candidat': candidat,
            'page_title': 'Paramètres du compte'
        })

    @http.route('/mon-espace/api/stats', type='json', auth='user', methods=['POST'])
    def get_candidat_stats(self, **kwargs):
        """API pour récupérer les statistiques du candidat (AJAX)"""
        try:
            candidat = request.env['website.user'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not candidat:
                return {'error': 'Candidat non trouvé'}

            stats = candidat.get_application_stats()
            stats.update({
                'profile_completion': candidat.profile_completion,
                'formations_count': len(candidat.formation_ids),
                'experiences_count': len(candidat.experience_ids),
                'trainings_count': len(candidat.training_ids)
            })
            
            return {'success': True, 'stats': stats}
            
        except Exception as e:
            _logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {'error': 'Erreur lors de la récupération des données'}

    @http.route('/mon-espace/delete-account', type='http', auth='user', methods=['POST'], csrf=True, website=True)
    def delete_account(self, **post):
        """Suppression du compte utilisateur"""
        try:
            if post.get('confirm_delete') != 'DELETE':
                return request.redirect('/mon-espace/settings?error=confirmation_required')
                
            candidat = request.env['website.user'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if candidat:
                # Désactiver plutôt que supprimer pour conserver l'historique
                candidat.write({'is_active': False})
                # Optionnel: supprimer l'utilisateur portal
                # candidat.user_id.unlink()
                
            return request.redirect('/web/session/logout')
            
        except Exception as e:
            _logger.error(f"Erreur lors de la suppression du compte: {e}")
            return request.redirect('/mon-espace/settings?error=delete_failed')

    # ===================================
    # MÉTHODES UTILITAIRES
    # ===================================
    
    def _prepare_candidat_context(self, candidat):
        """Prépare le contexte commun pour les templates"""
        return {
            'candidat': candidat,
            'stats': candidat.get_application_stats(),
            'profile_completion': candidat.profile_completion,
            'recent_applications': candidat.application_ids.sorted('create_date', reverse=True)[:5]
        }
    
    def _validate_form_data(self, post_data, required_fields=None):
        """Valide les données du formulaire"""
        errors = []
        
        if required_fields:
            for field in required_fields:
                if not post_data.get(field):
                    errors.append(f"Le champ {field} est obligatoire")
        
        # Validation email
        email = post_data.get('email')
        if email:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                errors.append("L'adresse email n'est pas valide")
        
        return errors