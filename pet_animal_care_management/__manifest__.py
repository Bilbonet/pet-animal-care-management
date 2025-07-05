# Copyright 2020 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pet Animal Care Management",
    "summary": "This module is the base for managing and caring for pets in Odoo.",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Management",
    "website": "https://github.com/Bilbonet/pet-animal-care-management",
    "author": "Jesus Ramiro (Bilbonet)",
    "maintainers": ["bilbonet"],
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "base",
        "mail",
        "hr",
        "product",
    ],
    "data": [
        "security/pet_animal_care_management_security.xml",
        "security/ir.model.access.csv",
        "data/pet_animal_care_management_sequence.xml",
        "views/pet_animal_views.xml",
        "views/pet_animal_type_views.xml",
        "views/hr_employee_view.xml",
        "views/veterinary_appointment_view.xml",
        "report/vet_appointment_report.xml",
        "data/vet_appointment_mail_template.xml",
    ],
}
