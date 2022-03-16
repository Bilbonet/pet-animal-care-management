# Copyright 2020Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _


class PetAimalType(models.Model):
    _name = "pet.animal.type"
    _description = "Pet Animal Type"

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('pet_animal_type_unique_code', 'UNIQUE (name)',
         _('The name for this type already exists, must be unique!')),
    ]


class PetAnimalSubType(models.Model):
    _name = "pet.animal.sub_type"
    _description = "Pet Animal Sub Type"

    name = fields.Char(string='Name', required=True)
    pet_type_id = fields.Many2one(string='Pet Type',
        comodel_name='pet.animal.type',  required=True)

