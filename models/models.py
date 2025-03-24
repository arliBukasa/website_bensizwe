# -*- coding: utf-8 -*-

from odoo import models, fields, api


class uptest(models.Model):
    _name = 'uptest.uptest'
    _description = 'uptest.uptest'

    name = fields.Char(string="Name")
    value = fields.Integer(string="Value 1")
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text(string="Description")
    image = fields.Binary(string="image")

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100
