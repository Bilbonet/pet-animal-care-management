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

#Create new Pet Information class.
class PetInformation(models.Model):
    _name = "pet.information"
    _description = "Pet Information"

    number = fields.Char(string='Pet Id',copy=False,readonly=True,index=True,default='New')
    name = fields.Char('Name')
    email = fields.Char('Email')
    mobile = fields.Char('Mobile')
    image_medium = fields.Binary("Medium-sized image", attachment=True)
    image_small = fields.Binary("Small-sized image", attachment=True)
    gender = fields.Selection([('male','Male'),('female','Female')],stirng="Gender")
    sex = fields.Selection([('male','Male'),('female','Female')],stirng="Sex")
    birth_date = fields.Date()
    pet_birth_date = fields.Date()
    pet_color_id = fields.Many2one('pet.color','Color')
    pet_type_id = fields.Many2one('pet.type','Type')
    pet_sub_type_id = fields.Many2one('pet.sub_type','Sub Type')
    veterinarian_id = fields.Many2one('hr.employee','Veterinarian')
    partner_id = fields.Many2one('res.partner','Client')
    pet_sub_type_ids = fields.Many2many('pet.sub_type')
    vaccine_ids = fields.One2many('vaccine.details','pet_information_id')
    food_ids = fields.One2many('pet.food','pet_information_id')

    #Create sequance number
    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].sudo().next_by_code('pet.information') or ' '
        vals['number'] = sequence
        result = super(PetInformation, self).create(vals)
        return result

    @api.onchange('pet_type_id')
    def onchange_pet_type_id(self):
        pet_sub_type_list = []
        for record in self:
            if record:
                pet_sub_ids = self.env['pet.sub_type'].search([('pet_type_id','=',record.pet_type_id.id)])
                if pet_sub_ids:
                    for pet_sub_type in pet_sub_ids:
                        if pet_sub_type:
                            pet_sub_type_list.append(pet_sub_type.id)
                            record.update({'pet_sub_type_ids':[(6,0,pet_sub_type_list)]})       

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for partner in self:
            if partner and partner.partner_id:
                email = partner.partner_id.email
                partner.email = email 
                mobile = partner.partner_id.mobile
                partner.mobile = mobile 
                birth_date = partner.partner_id.birth_date
                partner.birth_date = birth_date 
                gender = partner.partner_id.gender
                partner.gender = gender

#Create new Vaccine Details class.
class VaccineDetails(models.Model):
    _name = 'vaccine.details'
    _description = 'Vaccine Details'
    _rec_name = 'vaccine_id'

    vaccine_id = fields.Many2one('pet.vaccine')
    date = fields.Datetime('Date')
    vaccine_state = fields.Selection([('remaining','Remaining'),('done','Done')],stirng="State",default='remaining')

    pet_information_id = fields.Many2one('pet.information')

#Create new Pet Food class.
class PetFood(models.Model):
    _name = 'pet.food'
    _description = 'Pet Food'
    _rec_name = 'food_id'

    pet_information_id = fields.Many2one('pet.information')
    food_id = fields.Many2one('product.template','Food')
    day_ids = fields.Many2many('pet.days',string='Days')
   
