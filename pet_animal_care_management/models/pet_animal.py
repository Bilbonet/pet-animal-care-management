# Copyright 2022 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PetAnimal(models.Model):
    _name = 'pet.animal'
    _description = 'Pet Animal Information'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = 'name desc'
    _rec_name = 'complete_name'

    @api.depends("vet_appointment_ids")
    def _compute_vet_appointment_count(self):
        for pet in self:
            pet.vet_apmt_count = len(pet.vet_appointment_ids)

    name = fields.Char(string='Name', index=True,
        copy=False, help="Pet's name")
    complete_name = fields.Char(string="Full Name",
        compute='_compute_complete_name', store=True)
    pet_code = fields.Char(string='Pet Chip/Code',
        copy=False, index=True,
        help='Individual code identification of the pet animal. '
             'With dogs usually be the chip code.')
    passport = fields.Char(string='Passport',
        copy=False, index=True,
        help="A pet passport is a document that officially records information "
             "related to a specific animal.")
    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide"
             " the pet animal without removing it.")
    pet_birth_date = fields.Date(string="Date Of Birth")
    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('unknow', 'Unknow')], string="Sex", copy=False)
    sterilized = fields.Boolean(string="Sterilized")
    pet_type_id = fields.Many2one('pet.animal.type',string='Type')
    pet_sub_type_id = fields.Many2one('pet.animal.sub_type',string='Sub Type')
    veterinarian_id = fields.Many2one(string='Veterinarian', 
        comodel_name='hr.employee', tracking=True)
    partner_id = fields.Many2one('res.partner',
        string='Owner', tracking=True)
    company_id = fields.Many2one('res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    privacy_visibility = fields.Selection([
        ('followers', 'Veterinarian and followers'),
        ('employees', 'Visible by all employees'),],
        string='Privacy', default='employees', required=True,
        help="Holds visibility of the pet animal:\n"
             "- Veterinarian and followers: Only followers, veterinarian and managers "
             "can be able to see the pet animal\n"
             "- Visible by all employees: Only employees "
             "may see the pet animal\n")
    note = fields.Text(string='Notes')
    vet_appointment_ids = fields.One2many(string='Veterinarian Appointments',
        comodel_name='veterinary.appointment', inverse_name='animal_id', )
    vet_apmt_count = fields.Integer(string="Amount Vet Appointment",
        compute='_compute_vet_appointment_count', store=True)

    _sql_constraints = [
        ('pet_animal_unique_code', 'UNIQUE (pet_code)',
         _('The Pet Identification Code must be unique!')),
    ]

    @api.depends('name', 'partner_id')
    def _compute_complete_name(self):
        """ Forms complete name of location from parent location to child location. """
        if self.partner_id.name:
            self.complete_name = '%s (%s)' % (self.name, self.partner_id.name)
        else:
            self.complete_name = self.name

    @api.model
    def create(self, vals):
        if not vals.get('pet_code', False):
            vals['pet_code'] = \
                self.env['ir.sequence'].sudo().next_by_code('pet.animal')
        return super(PetAnimal, self).create(vals)

    def write(self, vals):
        if vals.get('pet_code', '/') == False:
            raise ValidationError(_('You cannot leave blank Pet Animal Code.'))
        return super(PetAnimal, self).write(vals)
