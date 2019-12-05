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

#New class Customer Invoice Report.
class CustomerInvoiceReport(models.AbstractModel):
    _name = 'report.abs_pet_animal_care_management.customer_invoice_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        cust_list = []
        customer_invoice_ids = self.env['account.invoice'].search([('type','=','out_invoice'),('date_invoice','>=',docs.start_date),('date_invoice','<=',docs.end_date),('state','=','paid')])
        if customer_invoice_ids:
            for customer_invoice_id in customer_invoice_ids:
                if customer_invoice_id:
                    cust_list.append(customer_invoice_id)
        if len(cust_list) > 0:
            docargs = {
                       'doc_ids': self.ids,
                       'doc_model': self.model,
                       'docs': docs,
                       'time': time,
                       'partner_ids':set(cust_list),
                       }
            if docargs:
                return docargs
        else:
            raise ValidationError("No Record Exist")
