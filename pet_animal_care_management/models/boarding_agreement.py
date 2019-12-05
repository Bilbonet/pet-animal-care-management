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

#Create new Boarding Agreement class.
class BoardingAgreement(models.Model):
    _name = "boarding.agreement"
    _description = "Boarding Agreement"
    _rec_name = 'number'

    number = fields.Char(string='Number',copy=False,readonly=True,index=True,default='New')
    drop_off_date = fields.Datetime('Drop Off Date')
    pick_up_date = fields.Datetime('Pick Up Date')
    mobile = fields.Char('Mobile')
    email = fields.Char('Email')
    total_days = fields.Integer('Days',compute='compute_count_days_hours')
    total_hours = fields.Integer('Hours',compute='compute_count_days_hours')
    invoice_count = fields.Integer('Invoiced',compute='compute_invoice_count')
    total_amount = fields.Float('Total Amount',compute='compute_total_amount')
    per_hour = fields.Float("Per Hour Amount")
    per_day = fields.Float("Per Day Amount")
    charges_type = fields.Selection([('hours','Hours'),('day','Day')],string='Charges Type')
    state = fields.Selection([('draft','Draft'),('request','Request'),('approved','Approved'),('invoiced','Invoiced'),
                              ('done','Done'),('rejected','Rejected'),('cancel','Discard')],"State",default='draft')    

    pet_boarding_id = fields.Many2one('pet.boarding', string = "I'm making an request for")
    partner_id = fields.Many2one('res.partner','Name Of Contact')
    boarding_pet_ids = fields.One2many('boarding.pets','boarding_agreement_id')


    @api.onchange('partner_id')
    def onchange_partner(self):
        for partner in self:
            if partner and partner.partner_id.id:
                mobile = partner.partner_id.mobile
                partner.mobile = mobile
                email = partner.partner_id.email
                partner.email = email

    @api.onchange('charges_type')
    def onchange_charges_type(self):
        for pet_boarding in self:
            if pet_boarding:
                boarding_id = self.env['pet.boarding'].search([('id','=',pet_boarding.pet_boarding_id.id)])
                if boarding_id:
                    if pet_boarding.charges_type == 'hours':
                        per_hour = boarding_id.per_hour
                        pet_boarding.per_hour = per_hour         
                    if pet_boarding.charges_type == 'day':
                        per_day = boarding_id.per_day
                        pet_boarding.per_day = per_day         


    @api.depends('drop_off_date','pick_up_date')
    def compute_count_days_hours(self):
        total = 0  
        if self.drop_off_date and self.pick_up_date:
            if self.drop_off_date <= self.pick_up_date:
                date12 = datetime.strptime(str(self.drop_off_date),'%Y-%m-%d %H:%M:%S')
                date1 = datetime.strptime(str(self.pick_up_date),'%Y-%m-%d %H:%M:%S')
                diff = date1 - date12
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                total_duration = hours
                self.total_hours = total_duration
                self.total_days = diff.days
            else:
                raise ValidationError("Invalid date period")

    @api.depends('total_days','total_hours','per_hour','per_day')
    def compute_total_amount(self):
        count = 0
        for record in self:
            if record:
                if self.charges_type == 'day':
                    count = (record.total_days * record.per_day)
                    record.total_amount = count   
                if self.charges_type == 'hours':
                    count = (record.total_hours * record.per_hour)
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
    def boarding_request(self):
        for rec in self:
            if rec and len(rec.boarding_pet_ids) != 0:
                sequence = self.env['ir.sequence'].sudo().next_by_code('boarding.agreement') or ' '
                if sequence:
                    rec.number = sequence
                    return self.write({'state':'request'})
            else:
                raise ValidationError('Please create some pet boarding lines.')

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

#Create new Boarding Pets class.
class BoardingPets(models.Model):
    _name = "boarding.pets"
    _description = "Boarding Pets"
    _rec_name = "pet_id"

    pet_sequence_id = fields.Char('Pet ID')

    pet_id = fields.Many2one('pet.information','Name')
    pet_color_id = fields.Many2one('pet.color','Color')
    pet_type_id = fields.Many2one('pet.type','Type')
    pet_sub_type_id = fields.Many2one('pet.sub_type','Sub Type')
    veterinarian_id = fields.Many2one('hr.employee','Veterinarian')
    boarding_agreement_id = fields.Many2one('boarding.agreement')

    @api.onchange('pet_sequence_id')
    def onchange_pet_sequence_id(self):
        for pet_sequence in self:
            if pet_sequence:
                pet_info_id = self.env['pet.information'].search([('number','=',pet_sequence.pet_sequence_id)])
                if pet_info_id:
                    pet_sequence.update({
                                        'pet_id'         :pet_info_id.id,
                                        'pet_type_id'    :pet_info_id.pet_type_id.id,
                                        'pet_sub_type_id':pet_info_id.pet_sub_type_id.id, 
                                        'pet_color_id'   :pet_info_id.pet_color_id.id,
                                        'veterinarian_id':pet_info_id.veterinarian_id.id,
                                       })
