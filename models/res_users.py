# -*- coding: utf-8 -*-
from odoo import models, fields, api
import secrets
import string
import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    # NOTE: Les champs de réinitialisation de mot de passe seront ajoutés plus tard
    # après mise à jour complète du module
    reset_password_token = fields.Char(string='Token de réinitialisation', copy=False)
    reset_password_token_expiry = fields.Datetime(string='Expiration du token', copy=False)
    
    def _generate_reset_token(self, user):
        """Génère un token unique pour la réinitialisation de mot de passe"""
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        
        # Définir l'expiration à 24 heures
        expiry = datetime.now() + timedelta(hours=24)
        
        # Sauvegarder le token et l'expiration
        user.sudo().write({
            'reset_password_token': token,
            'reset_password_token_expiry': expiry
        })
        
        _logger.info("Generated reset token for user %s: %s (expires: %s)", user.email, token, expiry)
        
        # Envoyer l'email
        user._send_reset_password_email(token)
        
        return token
    
    def _send_reset_password_email(self, token):
        """Envoie l'email de réinitialisation de mot de passe"""
        # URL de réinitialisation
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'http://localhost:8069')
        reset_url = f"{base_url}/candidat/reset_password/confirm?token={token}"
        
        try:
            # Pour le développement, on log simplement l'URL
            _logger.info("="*50)
            _logger.info("RESET PASSWORD EMAIL FOR: %s", self.email)
            _logger.info("Reset URL: %s", reset_url)
            _logger.info("Token: %s", token)
            _logger.info("="*50)

            # envoie avec smtplib email
            server = smtplib.SMTP('smtp.office365.com', 587)
            server.starttls()
            server.login('notification@bensizwe.com', 'Fug42481')
            subject = 'Réinitialisation de votre mot de passe - BenSizwe'
            body = f'''
                <h3>Réinitialisation de votre mot de passe</h3>
                <p>Bonjour {self.name},</p>
                <p>Cliquez sur ce lien pour réinitialiser votre mot de passe :</p>
                <p><a href="{reset_url}">Réinitialiser mon mot de passe</a></p>
            '''
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = 'notification@bensizwe.com'
            message['To'] = self.email
            message.attach(MIMEText(body, 'html'))
            server.sendmail('notification@bensizwe.com', self.email, message.as_string())

            # Envoi de l'email
            server.quit()

        except Exception as e:
            _logger.error("Failed to send reset password email to %s: %s", self.email, str(e))

    def _validate_reset_token(self, token):
        """Valide un token de réinitialisation"""
        if not token:
            return False
            
        # Rechercher l'utilisateur avec le token valide et non expiré
        user = self.sudo().search([
            ('reset_password_token', '=', token),
            ('reset_password_token_expiry', '>', datetime.now())
        ], limit=1)
        
        if user:
            _logger.info("Valid token found for user: %s", user.email)
            return user
        else:
            _logger.info("Invalid or expired token: %s", token)
            return False
    
    def _reset_password_with_token(self, token, new_password):
        """Réinitialise le mot de passe avec un token valide"""
        user = self._validate_reset_token(token)
        
        if not user:
            return False
            
        try:
            # Mettre à jour le mot de passe et supprimer le token
            user.sudo().write({
                'password': new_password,
                'reset_password_token': False,
                'reset_password_token_expiry': False
            })
            
            _logger.info("Password reset successfully for user %s", user.email)
            return user
            
        except Exception as e:
            _logger.error("Error resetting password for user %s: %s", user.email, str(e))
            return False