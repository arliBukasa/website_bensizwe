#-*- coding: utf-8 -*-
import json
import logging
import random

from odoo import http
from odoo.http import request
#2import yfinance as yf
from datetime import datetime as dt


class Main(http.Controller):

    @http.route('/jobs_row/', type='json', auth='public')
    def jobs_row(self, search=None, duree_contrat=None):
        domain = [("website_published","=",True)]
        if search:
            domain.append(('name', 'ilike', search))
        if duree_contrat:
            domain.append(('duree_contrat', '=',duree_contrat))
        jobs = request.env['hr.job'].sudo().search(domain, limit=15, order='write_date desc')
        return [{
            'name': j.name,
            'url': j.website_url,
            'localisation': j.localisation if j.localisation else '',
            'description': j.description,
            'write_date': j.write_date.strftime('%d/%m/%Y'),
            'date_cloture':j.date_cloture.isoformat() if j.date_cloture else '',
            'duree_contrat': j.duree_contrat or 'N/A'
        } for j in jobs]

    @http.route('/training_row', type='json', auth='public')
    def trainnings(self, **kw):

        # afficher les 15 derniers jobs selon la date d'expiration
        formations = request.env['website.training'].sudo().search([("is_published","=",True)], limit=3)
        liste_formations= []
        if formations:
            for formation in formations:
                # get the job's datas
                formation_data = {
                    'id': formation.id,
                    'name': formation.name,
                    'description': formation.description,
                    'date_start': formation.date_start,
                    'date_end': formation.date_end,
                    'header': formation.header,
                    'status': formation.status,
                    'cout': formation.cout,
                    'is_published': formation.is_published,
                    'url': '/formation/inscription/' + str(formation.id)                   
                }
                liste_formations.append(formation_data)
        return liste_formations
    
    #inscription a une formation
    @http.route('/formation/inscription/<int:id>', type='http', auth='public', website=True)
    def inscription_formation(self, id, **kw):
        formation = request.env['website.training'].sudo().search([('id', '=', id)])
        candidat = request.env['website.user'].sudo().search([('user_id', '=', request.env.user.id)])
        if not candidat:
            candidat = request.env['website.user'].sudo().create({
                'name': request.env.user.name,
                'user_id': request.env.user.id,
                'email': request.env.user.email,
                'phone': request.env.user.phone
            })

        logging.info(' ================== candidat: %s vs webuser : %s', candidat.user_id.id,request.website.user_id.id)
        return request.render('website_bensizwe.inscription_formation', {
            'formation': formation,
            'candidat': candidat,
            'website': request.website
        })
    
    # Route de validation de l'inscription
    @http.route('/formation/valider_inscription/<int:id>', type='http', auth='user', website=True)
    def valider_inscription(self, id, **kw):
        formation = request.env['website.training'].sudo().browse(id)
        candidat = request.env['website.user'].sudo().search([('user_id', '=', request.env.user.id)])

        if candidat and formation:
            # Ajoute la formation s'il n'est pas déjà inscrit
            if formation not in candidat.training_ids:
                candidat.write({'training_ids': [(4, formation.id)]})
            return request.render('website_bensizwe.confirmation_inscription', {
                'formation': formation,
                'candidat': candidat
            })
        return request.redirect('/candidat/login')
    
    """@http.route('/', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        jobs = request.env['hr.job'].sudo().search([], limit=6, order='create_date desc')
        formations = request.env['website.formation'].sudo().search([], limit=6, order='create_date desc')

        return request.render('website.homepage1', {
            'jobs': jobs,
            'formations': formations
        }) """
    
    @http.route('/jobs_row_out', type='json', auth='public')
    def list_out(self, **kw):

        # afficher les 15 derniers jobs selon la date d'expiration
        jobs = request.env['hr.job'].sudo().search([("website_published","=",True)], limit=15, order='write_date desc')
        row_jobs = []
        if jobs:
            for job in jobs:
                # get the job's datas
                job_data = {
                    'id': job.id,
                    'name': job.name,
                    'description': job.description,
                    'location': job.address_id.name,
                    'write_date': job.write_date,
                    'url': '/job/' + str(job.id)
                }
                row_jobs.append(job_data)
        return row_jobs
