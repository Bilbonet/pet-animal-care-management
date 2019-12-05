# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
from odoo import api,fields,models,_
from datetime import datetime
from odoo.exceptions import ValidationError
import re

#Create new Location Information class.
class LocationInformation(models.Model):
    _name = "location.information"
    _description = "Location Information"

    name = fields.Char('Name')
    street = fields.Char('Street')
    street2 = fields.Char('Street')
    city = fields.Char('City')
    zip = fields.Char('Zip')
    email = fields.Char('Email')
    mobile = fields.Char('Mobile')
    amount = fields.Float("Amount")
    capacity = fields.Float('Capacity')
    total_pet = fields.Float('Total Pets',compute='cal_pet')

    country_id = fields.Many2one('res.country')
    state_id = fields.Many2one('res.country.state')
    day_care_pet_ids = fields.One2many('pet.day_care','location_id')

    @api.constrains('email')
    def _check_values_tp(self):
        expr = "^[a-zA-Z0-9._+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9.]*\.*[a-zA-Z]{2,4}$"
        for val in self:
            if val.email:
                if re.match(expr, val.email) is not None:
                    pass
                else:
                    raise ValidationError('Please Enter Valid Email Id')

    @api.depends('day_care_pet_ids')
    def cal_pet(self):
        count = 0
        for rec in self:
            if rec:
                pet_day_care_ids = self.env['pet.day_care'].search([('location_id','=',rec.id),('state','in',['approved'])])
                if pet_day_care_ids:
                    for pet_id in pet_day_care_ids:
                        if pet_id.day_care_pet_ids:
                            for pet in pet_id.day_care_pet_ids:
                                if pet:    
                                    count = count + 1
                                    rec.total_pet = count
