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
    animal_weight = fields.Integer(string='Animal Weight')
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
