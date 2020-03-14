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
{
    'name': "Pet Animal Care Management",
    'author': 'Ascetic Business Solution',
    'category': 'Sales',
    'summary': """Pet Animal Care Management""",
    'website': 'http://www.asceticbs.com',
    'license': 'OPL-1',
    'description': """ """,
    'version': '12.0.1.0',
    'depends': ['base','sale_management','hr'],
    'data': [
             'security/abs_pet_animal_care_management_security.xml',
             'security/ir.model.access.csv',
             'wizard/create_invoice_view.xml',
             'wizard/day_care_create_invoice_view.xml',
             'wizard/customer_invoice_form_view.xml',
             'wizard/boarding_pet_category_view.xml',
             'wizard/day_care_pet_category_view.xml',    
             'views/res_partner_view.xml',
             'views/boarding_agreement_view.xml',
             'views/pet_day_care_view.xml',
             'views/pet_service_view.xml',    
             'views/pet_information_view.xml',  
             'views/hr_employee_view.xml',
             'views/pet_food_view.xml', 
             'views/product_template_view.xml',
             'views/location_information_view.xml',
             'views/pet_type_view.xml',
             'views/pet_sub_type_view.xml',
             'views/pet_vaccine_view.xml',
             'views/pet_color_view.xml',
             'views/pet_boarding_view.xml',
             'views/pet_days_view.xml',
             'views/customer_invoice_report_view.xml',
             'views/customer_invoice_template.xml',
             'views/boarding_pet_category_wise_report_view.xml',
             'views/boarding_pet_category_wise_template.xml',
             'views/day_care_pet_category_wise_report_view.xml',
             'views/day_care_pet_category_wise_template.xml',   
             'data/boarding_pet_charges_view.xml',
             'data/day_care_pet_charges_view.xml',
             'data/service_charges_view.xml',   
            ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
