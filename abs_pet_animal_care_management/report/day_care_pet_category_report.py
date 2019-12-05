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

#New class Day Care Pet Category Wise Report.
class DayCarePetReport(models.AbstractModel):
    _name = 'report.abs_pet_animal_care_management.day_care_category_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        pet_category_list = []
        day_care_ids = self.env['pet.day_care'].search([('pick_up_date','>=',docs.start_date),('pick_up_date','<=',docs.end_date),('state','=','approved')])
        if day_care_ids:
            for day_care_id in day_care_ids:
                if day_care_id:
                    for pet in day_care_id.day_care_pet_ids:
                        if pet and pet.pet_type_id:
                            pet_category_list.append(pet)
        if len(pet_category_list) > 0:
            docargs = {
                       'doc_ids': self.ids,
                       'doc_model': self.model,
                       'docs': docs,
                       'time': time,
                       'day_care_category_ids':set(pet_category_list),
                       }
            if docargs:
                return docargs
        else:
            raise ValidationError("No Record Exist")
