# Copyright 2020Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class PetAimalType(models.Model):
    _name = "pet.animal.type"
    _description = "Pet Animal Type"

    name = fields.Char(String='Name', required=True)

    _sql_constraints = [
        ('pet_animal_type_unique_code', 'UNIQUE (name)',
         _('The name for this type already exists, must be unique!')),
    ]


class PetAnimalSubType(models.Model):
    _name = "pet.animal.sub_type"
    _description = "Pet Animal Sub Type"

    name = fields.Char(String='Name', required=True)
    pet_type_id = fields.Many2one('pet.animal.type', strin='Pet Type', required=True)

