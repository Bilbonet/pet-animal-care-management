# Copyright 2020Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class PetAnimal(models.Model):
    _name = 'pet.animal'
    _description = 'Pet Animal Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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
        ('unknow', 'Unknow')], stirng="Sex", copy=False)
    sterilized = fields.Boolean(string="Sterilized")
    image = fields.Binary(string="Big-sized image", attachment=True,
        help="This field holds the image used as image for the pet animal, "
             "limited to 1024x1024px.")
    image_medium = fields.Binary(string='Medium-sized image', attachment=True,
        help="Medium-sized image of the pet animal. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(string='Small-sized image', attachment=True,
        help="Small-sized image of the pet animal. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    pet_type_id = fields.Many2one('pet.animal.type',string='Type')
    pet_sub_type_id = fields.Many2one('pet.animal.sub_type',string='Sub Type')
    veterinarian_id = fields.Many2one('hr.employee',
        string='Veterinarian', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner',
        string='Owner', track_visibility='onchange')
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

    @api.one
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
        tools.image_resize_images(vals)
        return super(PetAnimal, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('pet_code', '/') == False:
            raise ValidationError(_('You cannot leave blank Pet Animal Code.'))
        tools.image_resize_images(vals)
        return super(PetAnimal, self).write(vals)
