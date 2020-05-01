# Copyright 2020Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class VeterinaryAppointment(models.Model):
    _name = "veterinary.appointment"
    _description = "Veterinary Appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "date_appointment desc"

    @api.returns('self')
    def _default_veterinarian_get(self):
        return self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid),
            ('veterinarian', '=', True)
        ], limit=1)

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
    animal_id = fields.Many2one('pet.animal',
        string='Pet Animal', required=True, track_visibility='onchange')
    partner_id = fields.Many2one(related="animal_id.partner_id",
        string='Owner')
    veterinarian_id = fields.Many2one('hr.employee',
        string='Veterinarian', default=_default_veterinarian_get,
        required=True, track_visibility='onchange')
    date_appointment = fields.Datetime(string='Date of Appointment',
        track_visibility='onchange', copy=False)
    history = fields.Text(string="Clinic History")
    diagnostic = fields.Text(string="Diagnostic")
    treatment = fields.Text(string="Treatment")
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
