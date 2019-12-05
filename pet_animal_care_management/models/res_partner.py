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

#Inherit Prtner class.
class Partner(models.Model):
    _inherit = "res.partner"
    _description = "Res Partner"

    birth_date = fields.Date('Birth Date')
    gender = fields.Selection([('male','Male'),('female','Female')],stirng="Gender")
    pet_ids = fields.One2many('pet.information','partner_id')
    pet_boarding_ids = fields.One2many('boarding.agreement','partner_id')
    pet_day_care_ids = fields.One2many('pet.day_care','partner_id')
    pet_service_ids = fields.One2many('pet.service','partner_id')  
