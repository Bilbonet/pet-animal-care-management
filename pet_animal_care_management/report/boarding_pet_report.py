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
from odoo import api, models, fields
from datetime import datetime 
from datetime import date
from odoo.exceptions import ValidationError
import time

#New class Boarding Pet Report.
class BoardingPetReport(models.AbstractModel):
    _name = 'report.abs_pet_animal_care_management.boarding_pet_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        pet_category_list = []
        boarding_ids = self.env['boarding.agreement'].search([('pick_up_date','>=',docs.start_date),('pick_up_date','<=',docs.end_date),('state','=','approved')])
        if boarding_ids:
            for boarding_id in boarding_ids:
                if boarding_id:
                    for pet in boarding_id.boarding_pet_ids:
                        if pet and pet.pet_type_id:
                            pet_category_list.append(pet)
        if len(pet_category_list) > 0:
            docargs = {
                       'doc_ids': self.ids,
                       'doc_model': self.model,
                       'docs': docs,
                       'time': time,
                       'category_ids':set(pet_category_list),
                       }
            if docargs:
                return docargs
        else:
            raise ValidationError("No Record Exist")
