# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from collections import OrderedDict


class CandidatePortal(CustomerPortal):
    """Extension du portail pour les candidats"""

    def _prepare_portal_layout_values(self):
        """Ajouter les informations des formations dans le portail"""
        values = super(CandidatePortal, self)._prepare_portal_layout_values()
        
        if request.env.user.is_candidate:
            # Compter les inscriptions aux formations
            formation_count = request.env['website.training.registration'].search_count([
                ('user_id', '=', request.env.user.id)
            ])
            values['formation_count'] = formation_count
            
        return values

    def _prepare_home_portal_values(self, counters):
        """Ajouter les formations dans les compteurs de la page d'accueil du portail"""
        values = super()._prepare_home_portal_values(counters)
        
        if 'formation_count' in counters and request.env.user.is_candidate:
            formation_count = request.env['website.training.registration'].search_count([
                ('user_id', '=', request.env.user.id)
            ])
            values['formation_count'] = formation_count
            
        return values

    @http.route(['/my/formations', '/my/formations/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_formations(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content', **kw):
        """Page des formations du candidat dans le portail"""
        
        if not request.env.user.is_candidate:
            return request.redirect('/my')

        values = self._prepare_portal_layout_values()
        
        # Configuration de recherche et tri
        searchbar_sortings = {
            'date': {'label': 'Date d\'inscription', 'order': 'registration_date desc'},
            'name': {'label': 'Nom de formation', 'order': 'training_id'},
            'state': {'label': 'Statut', 'order': 'state'},
        }
        
        searchbar_inputs = {
            'content': {'input': 'content', 'label': 'Rechercher dans formations'},
        }
        
        # Valeurs par défaut
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Domaine de recherche
        domain = [('user_id', '=', request.env.user.id)]
        
        if search and search_in:
            if search_in == 'content':
                domain += [('training_id.name', 'ilike', search)]
        
        if date_begin and date_end:
            domain += [('registration_date', '>=', date_begin), ('registration_date', '<=', date_end)]

        # Compter les enregistrements
        formation_count = request.env['website.training.registration'].search_count(domain)
        
        # Configuration du pager
        pager = portal_pager(
            url="/my/formations",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in, 'search': search},
            total=formation_count,
            page=page,
            step=self._items_per_page
        )
        
        # Récupérer les inscriptions
        formations = request.env['website.training.registration'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'formations': formations,
            'page_name': 'formation',
            'archive_groups': [],
            'default_url': '/my/formations',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
        })
        
        return request.render("website_bensizwe.portal_my_formations", values)

    @http.route(['/my/formation/<int:registration_id>'], type='http', auth="user", website=True)
    def portal_formation_detail(self, registration_id, access_token=None, **kw):
        """Détail d'une inscription à une formation"""
        
        try:
            registration = self._document_check_access('website.training.registration', registration_id, access_token)
        except:
            return request.redirect('/my')
            
        # Vérifier que c'est bien l'inscription de l'utilisateur
        if registration.user_id.id != request.env.user.id:
            return request.redirect('/my')

        values = {
            'registration': registration,
            'formation': registration.training_id,
            'user': request.env.user,
            'page_name': 'formation',
        }
        
        return request.render("website_bensizwe.portal_formation_detail", values)
