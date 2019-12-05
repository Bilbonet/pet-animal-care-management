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
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

#New class for Customer Invoice. 
class CustomerInvoice(models.TransientModel):
    _name = "customer.invoice"
    _description = "Customer Invoice"

    start_date = fields.Date("From date")  
    end_date = fields.Date(string="To date")

    #Function for Print report.
    @api.multi
    def print_report(self):
        if self.start_date and self.end_date:
            if self.start_date < self.end_date:
                data = {}
                data['form'] = self.read(['start_date','end_date'])
                return self.env.ref('abs_pet_animal_care_management.action_customer_invoice_report').report_action(self, data=data, config=False)  
            else:
                raise ValidationError("Invalid date period")
