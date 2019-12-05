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
from datetime import date

#create new CreateInvoice Class.
class CreateInvoice(models.TransientModel):
    _name = "create.invoice"

    boarding_id = fields.Many2one('boarding.agreement',string='Pet Boarding Id')
    main_amount = fields.Float('Total Amount',compute="count_main_amount")
    total_days = fields.Integer('Days')
    total_hours = fields.Integer('Hours')
    total_amount = fields.Float('Amount')
    total_pets = fields.Integer('Total Pet',compute="count_total_pets")

    partner_id = fields.Many2one('res.partner','Client')
    boarding_ids = fields.Many2many('boarding.pets',string='Pets')

    #create a function for update data in fields. 
    @api.model
    def default_get(self, fields):
        rec = super(CreateInvoice, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        boarding = self.env['boarding.agreement'].search([('id','=',active_ids)])
        amount = 0
        pet_list = []
        if boarding:
             for record in boarding:
                 if record:
                     for pet in record.boarding_pet_ids:
                         if pet:
                             pet_list.append(pet.id)
                     rec.update({
                                 'boarding_id':record.id,
                                 'partner_id':record.partner_id.id,
                                 'boarding_ids':[(6, 0, pet_list)],  
                                 'total_amount':record.total_amount,
                                })   
        return rec

    @api.depends('boarding_ids') 
    def count_total_pets(self):
        count = 0
        for pets in self.boarding_ids:
            if pets:
                count = count + 1
                self.total_pets = count   

    @api.depends('total_pets') 
    def count_main_amount(self):
        total = 0
        for record in self:
            if record and record.total_pets:
                total = (record.total_pets * record.total_amount)
                record.main_amount = total   

    def create_invoice(self):
        invoice_dict = {}
        invoice_line_dict ={}
        today_date = date.today()
        active_ids = self._context.get('active_ids')
        boarding = self.env['boarding.agreement'].browse(active_ids)
        product = self.env.ref('abs_pet_animal_care_management.charges_product')
        ir_property_obj = self.env['ir.property']
        account_id = False
        account_invoice_object = self.env['account.invoice']
        account_invoice_line_object = self.env['account.invoice.line']
        for record in self:
            if record:
                invoice_dict = {
                                'partner_id':record.partner_id.id,
                                'date_invoice':today_date,
                                'name':record.boarding_id.number,
                               }
                if invoice_dict:
                    invoice = account_invoice_object.create(invoice_dict)
                if account_id:
                    inc_acc = product.property_account_income_id.id
                if not account_id:
                    inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')

                invoice_line_dict = {
                                         'invoice_id':invoice.id,
                                         'product_id':product.id,
                                         'price_unit':record.main_amount,
                                         'account_id':inc_acc.id, 
                                         'name':product.name
                                    }
                if invoice_line_dict:
                    account_invoice_line_object.create(invoice_line_dict)
                    boarding.write({'state':'invoiced'})
