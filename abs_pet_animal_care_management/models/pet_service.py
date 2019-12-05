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
from odoo.exceptions import ValidationError

#Create new Pet Service class.
class PetService(models.Model):
    _name = "pet.service"
    _description = "Pet Service"
    _rec_name = "number" 

    number = fields.Char(string='Number',copy=False,readonly=True,index=True,default='New')
    mobile = fields.Char('Mobile')
    email = fields.Char('Email')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    invoice_count = fields.Integer('Invoiced',compute='compute_invoice_count')
    amount_total = fields.Float('Total Amount',compute='cal_amount_total')
    state = fields.Selection([('draft','Draft'),('request','Request'),('approved','Approved'),('invoiced','Invoiced'),
                              ('done','Done'),('rejected','Rejected'),('cancel','Discard')],"State",default='draft')

    pet_service_ids = fields.One2many('pet.services','pet_service_id',string = 'Pet') 
    partner_id = fields.Many2one('res.partner','Client')

    @api.onchange('partner_id')
    def onchange_partner(self):
        for partner in self:
            if partner and partner.partner_id.id:
                mobile = partner.partner_id.mobile
                partner.mobile = mobile
                email = partner.partner_id.email
                partner.email = email

    @api.depends('pet_service_ids.amount')
    def cal_amount_total(self):
        total = 0
        for record in self:
            if record:
                for pet_service in record.pet_service_ids:
                    if pet_service:
                        total = total + pet_service.amount
                        record.amount_total = total

    @api.multi
    def service_request(self):
        for rec in self:
            if rec and len(rec.pet_service_ids) != 0:
                sequence = self.env['ir.sequence'].sudo().next_by_code('pet.service') or ' '
                if sequence:
                    rec.number = sequence
                    return self.write({'state':'request'})
            else:
                raise ValidationError('Please create some pet service lines.')

    @api.multi
    def approve_request(self):
        return self.write({'state':'approved'})

    @api.multi
    def reject_request(self):
        return self.write({'state':'rejected'})

    @api.multi
    def cancel_request(self):
        return self.write({'state':'cancel'})

    @api.multi
    def back_to_draft(self):
        return self.write({'state':'draft'})

    @api.multi
    def action_done(self):
        for record in self:
            if record:
                invoice_ids = self.env['account.invoice'].search([('partner_id','=',record.partner_id.id),('name','=',record.number)])
                for invoice_id in invoice_ids:
                    if invoice_id:
                        if invoice_id.state == 'paid':
                            self.write({'state':'done'})
                        else:
                            raise ValidationError('Pay Remaining Amount.')

    #create invoice For Salon and Spa Charges. 
    def create_invoice(self):
        invoice_dict = {}
        invoice_line_dict = {}
        today_date = date.today()
        product = self.env.ref('abs_pet_animal_care_management.service_charges')
        ir_property_obj = self.env['ir.property']
        account_id = False
        account_invoice_object = self.env['account.invoice']
        account_invoice_line_object = self.env['account.invoice.line']
        for record in self:
            if record:
                invoice_dict = {
                                'partner_id':record.partner_id.id,
                                'date_invoice':today_date,
                                'name':record.number,
                               }
                if invoice_dict:
                    invoice = account_invoice_object.create(invoice_dict)
                if account_id:
                    inc_acc = product.property_account_income_id.id
                if not account_id:
                    inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
                if invoice: 
                    invoice_line_dict = {
                                         'invoice_id':invoice.id,
                                         'product_id':product.id,
                                         'price_unit':record.amount_total,
                                         'account_id':inc_acc.id, 
                                         'name':product.name
                                    }
                    if invoice_line_dict:
                        account_invoice_line_object.create(invoice_line_dict)
                        record.write({'state':'invoiced'})

    #Action for count invoices.
    def compute_invoice_count(self):
        account_invoice_object = self.env['account.invoice']
        for count in self:
            if count:
                count.invoice_count = account_invoice_object.search_count([('partner_id','=',count.partner_id.id),('name','=',count.number)])

    #Action for Invoice view.
    @api.multi
    def action_invoice(self):
        return {
                'name': _('Invoices'),
                'type': 'ir.actions.act_window',
                'domain':[('partner_id','=',self.partner_id.id),('name','=',self.number)],
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'view_id': 'False',
                'views':[(self.env.ref("account.invoice_tree").id,'tree'),(self.env.ref("account.invoice_form").id,'form')],
                'target': 'current',
               }


#Create new Day Care Pets class.
class PetServices(models.Model):
    _name = "pet.services"
    _description = "Pet Services"
    _rec_name = "pet_id"

    pet_service_sequence_id = fields.Char('Pet ID')
    amount = fields.Float('Amount')

    pet_id = fields.Many2one('pet.information','Name')
    pet_sub_type_id = fields.Many2one('pet.sub_type','Sub Type')
    pet_service_id = fields.Many2one('pet.service')
    service_ids = fields.Many2many('product.template',string='Services')

    @api.onchange('pet_service_sequence_id')
    def onchange_pet_sequence_id(self):
        for pet_sequence in self:
            if pet_sequence:
                pet_info_id = self.env['pet.information'].search([('number','=',pet_sequence.pet_service_sequence_id)])
                if pet_info_id:
                    pet_sequence.update({
                                        'pet_id'         :pet_info_id.id,
                                        'pet_sub_type_id':pet_info_id.pet_sub_type_id.id, 
                                       })

    @api.onchange('service_ids')
    def onchange_service_ids(self):
        count = 0
        for record in self:
            if record:
                for rec in record.service_ids:
                    if rec:
                        count = count + rec.list_price
                        record.amount = count
