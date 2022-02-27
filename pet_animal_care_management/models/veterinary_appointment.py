# Copyright 2020Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VeterinaryAppointment(models.Model):
    _name = "veterinary.appointment"
    _description = "Veterinary Appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "date_appointment desc"

    @api.returns('self', lambda value: value.id if value else False)
    def _default_veterinarian_get(self):
        return self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid),
            ('veterinarian', '=', True)
        ], limit=1)

    @api.returns('self', lambda value: value.id if value else False)
    def _default_partner_get(self):
        if self.animal_id and not self.partner_id:
            return self.animal_id.partner_id
        
    name = fields.Char(string='Name',
        required=True, default="/", readonly=True)
    active = fields.Boolean(default=True, copy=False,
        help="If the active field is set to False, it will allow you to hide"
        " the veterinary appointment without removing it.")
    company_id = fields.Many2one('res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    state = fields.Selection(
        [('draft','Pending'),
        ('done','Done'),
        ('cancel','Cancel')],
        string='Status', required=True, index=True, default='draft',
        track_visibility='onchange', copy=False)
    animal_id = fields.Many2one(string='Pet Animal',
        comodel_name='pet.animal', readonly=True, 
        states={'draft': [('readonly', False)]}, 
        track_visibility='onchange')
    partner_id = fields.Many2one('res.partner',
        string='Customer', default=_default_partner_get,
        states={'draft': [('readonly', False)]})
    veterinarian_id = fields.Many2one('hr.employee',
        string='Veterinarian', default=_default_veterinarian_get,
        required=True, states={'done': [('readonly', True)]}, track_visibility='onchange')
    date_appointment = fields.Datetime(string='Date of Appointment',
        states={'done': [('required', True),('readonly', True)]},
        track_visibility='onchange', copy=False)
    history = fields.Text(string="Clinic History",
        readonly=True, states={'draft': [('readonly', False)]})
    diagnostic = fields.Text(string="Diagnostic",
        readonly=True, states={'draft': [('readonly', False)]})
    treatment = fields.Text(string="Treatment",
        readonly=True, states={'draft': [('readonly', False)]})
    animal_weight = fields.Float(string='Animal Weight')
    privacy_visibility = fields.Selection([
        ('followers', 'Veterinarian and followers'),
        ('employees', 'Visible by all employees'),],
        string='Privacy', default='employees', required=True,
        help="Holds visibility of the vet appointment:\n"
             "- Veterinarian and followers: Only followers, veterinarian and managers "
             "can be able to see the pet animal\n"
             "- Visible by all employees: Only employees "
             "may see the pet animal\n")

    @api.onchange('state')
    def _onchnge_state(self):
        if not self.date_appointment and self.state != 'draft':
            raise ValidationError(
                _("You must set a datetime for the appointment."))
        pass

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id and not self.animal_id:
            animal = self.env['pet.animal'].search([
                        ('partner_id', '=', self.partner_id.id),
                        ('active', '=', True)
                    ], limit=1)
            if animal:
                self.animal_id = animal
        
    @api.onchange('animal_id')
    def _onchange_animal(self):
        if self.animal_id and not self.partner_id:
            self.partnet_id = self.animal_id.partner_id

    @api.model
    def create(self, vals):
        # context: no_log, because subtype already handle this
        context = dict(self.env.context, mail_create_nolog=True)

        # Assign new code
        if vals.get('name', '/') == '/':
            vals['name'] = \
                self.env['ir.sequence'].next_by_code('veterinary.appointment')

        va = super(VeterinaryAppointment, self.with_context(context)).create(vals)
        return va

    @api.multi
    def action_vet_appointment_send(self):
        '''
        This function opens a window to compose an email,
        with the vet appointment template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'pet_animal_care_management', 'vet_appointment_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        lang = self.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(
                template.lang, 'veterinary.appointment', self.ids[0])
        ctx = {
            'default_model': 'veterinary.appointment',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'model_description': self.with_context(lang=lang).name,
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def send_vet_appointment_reminder(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'pet_animal_care_management', 'vet_appointment_email_reminder')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        lang = self.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(
                template.lang, 'veterinary.appointment', self.ids[0])
        ctx = {
            'default_model': 'veterinary.appointment',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'model_description': self.with_context(lang=lang).name,
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }