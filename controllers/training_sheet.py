from odoo import http, fields
from odoo.http import request, content_disposition


class TrainingSheetController(http.Controller):

    @http.route('/website_bensizwe/fiche_formations', type='http', auth='user')
    def training_sheet(self, ids='', **kwargs):
        """Fiche Excel des participants : un onglet par formation. Réservé au personnel (pas au portail)."""
        if not request.env.user.has_group('base.group_user'):
            return request.not_found()
        id_list = [int(i) for i in ids.split(',') if i.strip().isdigit()]
        trainings = request.env['website.training'].browse(id_list).exists()
        if not trainings:
            return request.not_found()
        content = trainings._participant_sheet_xlsx()
        filename = 'Fiche_formations_%s.xlsx' % fields.Date.context_today(trainings).strftime('%Y%m%d')
        return request.make_response(content, headers=[
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', content_disposition(filename)),
        ])
