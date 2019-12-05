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
from datetime import date,datetime
from odoo.exceptions import ValidationError

#Create new Pet Day Care class.
class PetBoarding(models.Model):
    _name = "pet.day_care"
    _description = "Pet Day Care"
    _rec_name = "number"

    number = fields.Char(string='Number',copy=False,readonly=True,index=True,default='New')
    drop_off_date = fields.Datetime('Drop Off Date')
    pick_up_date = fields.Datetime('Pick Up Date')
    mobile = fields.Char('Mobile')
    email = fields.Char('Email')
    amount = fields.Float('Amount')
    total_days = fields.Integer('Days',compute='compute_count_days')
    invoice_count = fields.Integer('Invoiced',compute='compute_invoice_count')
    total_amount = fields.Float('Total Amount',compute='compute_total_amount')
    state = fields.Selection([('draft','Draft'),('request','Request'),('approved','Approved'),('invoiced','Invoiced'),
                              ('done','Done'),('rejected','Rejected'),('cancel','Discard')],"State",default='draft')

    partner_id = fields.Many2one('res.partner','Client')
    location_id = fields.Many2one('location.information','Location')
    day_care_pet_ids = fields.One2many('day_care.pets','day_care_id',string = 'Pet')

    @api.onchange('partner_id')
    def onchange_partner(self):
        for partner in self:
            if partner and partner.partner_id.id:
                mobile = partner.partner_id.mobile
                partner.mobile = mobile
                email = partner.partner_id.email
                partner.email = email

    @api.onchange('location_id')
    def onchange_location_id(self):
        for location in self:
            if location and location.location_id.id:
                amount = location.location_id.amount
                location.amount = amount

    @api.depends('drop_off_date','pick_up_date')
    def compute_count_days(self):
        total = 0  
        if self.drop_off_date and self.pick_up_date:
            if self.drop_off_date < self.pick_up_date:
                date12 = datetime.strptime(str(self.drop_off_date),'%Y-%m-%d %H:%M:%S')
                date1 = datetime.strptime(str(self.pick_up_date),'%Y-%m-%d %H:%M:%S')
                total = date1.date() - date12.date()  
                self.total_days = total.days
            else:
                raise ValidationError("Invalid date period")

    @api.depends('total_days','amount')
    def compute_total_amount(self):
        count = 0
        for record in self:
            if record and record.total_days:
                count = (record.total_days * record.amount)
                record.total_amount = count

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


    @api.multi
    def day_care_request(self):
        count = 0
        total = 0  
        for rec in self:
            if rec and len(rec.day_care_pet_ids) != 0:
                sequence = self.env['ir.sequence'].sudo().next_by_code('pet.day_care') or ' '
                if sequence:
                    rec.number = sequence
                    location_pet_ids = self.env['location.information'].search([('id','=',rec.location_id.id)])
                    if location_pet_ids:
                        for location_pet_id in location_pet_ids:
                            if location_pet_id:
                                for pet in location_pet_id.day_care_pet_ids:
                                    if pet and pet.state == 'draft':
                                        if pet.day_care_pet_ids:
                                            for pet_id in pet.day_care_pet_ids:
                                                if pet_id:
                                                    count = count + 1
                                                    if location_pet_id.capacity >= count:
                                                        self.write({'state':'request'})
                                                    if location_pet_id.capacity < count:
                                                        raise ValidationError("You can not request more than {} pet."
                                                                               .format(int(location_pet_id.capacity)))
                                    if pet and pet.state in ['request','approved']:
                                        if pet.day_care_pet_ids:
                                            for pet_animal in pet.day_care_pet_ids:
                                                if pet_animal:
                                                    total = total + 1
                                                    if location_pet_id.capacity >= total:
                                                        rec.state = 'request'
                                                    if location_pet_id.capacity < total:
                                                        raise ValidationError("This Location {} has already have {} pets. You can not request more than {} pet."
                                                              .format(location_pet_id.name,int(location_pet_id.total_pet),
                                                                      int(location_pet_id.capacity)))
            else:
                raise ValidationError('Please create some pet day care lines.')
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

#Create new Day Care Pets class.
class DayCarePets(models.Model):
    _name = "day_care.pets"
    _description = "Day Care Pets"
    _rec_name = "pet_id"

    pet_day_sequence_id = fields.Char('Pet ID')

    pet_id = fields.Many2one('pet.information','Name')
    pet_color_id = fields.Many2one('pet.color','Color')
    pet_type_id = fields.Many2one('pet.type','Type')
    pet_sub_type_id = fields.Many2one('pet.sub_type','Sub Type')
    veterinarian_id = fields.Many2one('hr.employee','Veterinarian')
    day_care_id = fields.Many2one('pet.day_care')

    @api.onchange('pet_day_sequence_id')
    def onchange_pet_sequence_id(self):
        for pet_sequence in self:
            if pet_sequence:
                pet_info_id = self.env['pet.information'].search([('number','=',pet_sequence.pet_day_sequence_id)])
                if pet_info_id:
                    pet_sequence.update({
                                        'pet_id'         :pet_info_id.id,
                                        'pet_type_id'    :pet_info_id.pet_type_id.id,
                                        'pet_sub_type_id':pet_info_id.pet_sub_type_id.id, 
                                        'pet_color_id'   :pet_info_id.pet_color_id.id,
                                        'veterinarian_id':pet_info_id.veterinarian_id.id,
                                       })
