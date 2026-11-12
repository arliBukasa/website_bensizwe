import io
import re
from datetime import date

import xlsxwriter

from odoo import models, fields, _
from odoo.exceptions import UserError

# Colonnes de la fiche, dans l'ordre demandé (une feuille Excel par formation)
SHEET_HEADERS = [
    'Année', 'Lieu de la formation', 'Province', 'Nom & Postnom du candidat', 'Prénom du candidat', 'Sexe',
    'Téléphone du candidat', 'Nom de la formation', 'Date fin formation', 'Nom du formateur',
    'Numéro de référence certificat',
]
SHEET_WIDTHS = [8, 24, 14, 32, 20, 6, 18, 38, 14, 22, 24]
SEXES = {'male': 'M', 'female': 'F'}


def _sheet_name(name, used):
    """Nom d'onglet valide pour Excel : 31 caractères maximum, sans []:*?/\\, unique dans le classeur."""
    base = re.sub(r'[\[\]:*?/\\]', '-', name or '').strip().strip("'")[:31] or 'Formation'
    candidate, n = base, 2
    while candidate.lower() in used:
        suffix = ' (%d)' % n
        candidate = base[:31 - len(suffix)] + suffix
        n += 1
    used.add(candidate.lower())
    return candidate


class WebsiteTrainingSheet(models.Model):
    _inherit = 'website.training'

    training_place = fields.Char(string='Lieu de la formation', default='Kinshasa')
    province = fields.Char(string='Province', default='Kinshasa')

    def _participant_sheet_rows(self):
        """Une ligne par participant (inscription au statut Participant), triée par nom."""
        self.ensure_one()
        ref_date = self.date_end or self.date_start
        rows = []
        participants = self.registration_ids.filtered(lambda r: r.state == 'confirmed')
        for reg in participants.sorted(lambda r: (r.candidat_id.name or '').lower()):
            candidat, certificate = reg.candidat_id, reg.certificate_ids[:1]
            year_date = ref_date or certificate.issue_date
            # Nom & Postnom / Prénom : champs séparés s'ils sont renseignés, sinon le nom complet en entier
            last_name = (candidat.last_name or '').strip() or (candidat.name or '').strip()
            rows.append([
                year_date.year if year_date else '',
                self.training_place or certificate.place or '',
                self.province or '',
                last_name,
                (candidat.first_name or '').strip(),
                SEXES.get(candidat.gender, ''),
                candidat.phone or '',
                self.name or '',
                self.date_end or certificate.date_end or False,
                certificate.trainer_name or self.trainer_name or '',
                certificate.code or '',
            ])
        return rows

    def _participant_sheet_xlsx(self):
        """Classeur Excel : un onglet par formation (dans l'ordre des dates de début)."""
        output = io.BytesIO()
        book = xlsxwriter.Workbook(output, {'in_memory': True})
        head = book.add_format({'bold': True, 'font_color': '#FFFFFF', 'bg_color': '#0B2A5C', 'border': 1,
                                'text_wrap': True, 'valign': 'vcenter', 'align': 'center'})
        cell = book.add_format({'border': 1, 'valign': 'vcenter'})
        day = book.add_format({'border': 1, 'valign': 'vcenter', 'num_format': 'dd/mm/yyyy'})
        used = set()
        for training in self.sorted(lambda t: (t.date_start or date.min, t.id)):
            sheet = book.add_worksheet(_sheet_name(training.name, used))
            sheet.set_row(0, 32)
            for col, (title, width) in enumerate(zip(SHEET_HEADERS, SHEET_WIDTHS)):
                sheet.set_column(col, col, width)
                sheet.write_string(0, col, title, head)
            rows = training._participant_sheet_rows()
            for r, row in enumerate(rows, start=1):
                for col, value in enumerate(row):
                    if isinstance(value, date):
                        sheet.write_datetime(r, col, value, day)
                    elif value in (False, None, ''):
                        sheet.write_blank(r, col, None, cell)
                    elif isinstance(value, int):
                        sheet.write_number(r, col, value, cell)
                    else:
                        # Texte (téléphone compris) : Excel ne doit pas le convertir en nombre
                        sheet.write_string(r, col, str(value), cell)
            sheet.freeze_panes(1, 0)
            sheet.autofilter(0, 0, max(len(rows), 1), len(SHEET_HEADERS) - 1)
        book.close()
        return output.getvalue()

    def action_export_participant_sheet(self):
        if not self:
            raise UserError(_("Aucune formation sélectionnée."))
        return {
            'type': 'ir.actions.act_url',
            'url': '/website_bensizwe/fiche_formations?ids=%s' % ','.join(str(i) for i in self.ids),
            'target': 'self',
        }
