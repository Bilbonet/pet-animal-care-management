# Copyright 2020Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Hr(models.Model):
    _inherit = "hr.employee"
    _description = "Hr Employee"

    veterinarian = fields.Boolean(string='Is Veterinarian')
