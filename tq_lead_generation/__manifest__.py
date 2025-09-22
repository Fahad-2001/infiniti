{
    'name': "Lead Generation",

    'summary': """""",
    'author': "Fahad Rizwan",
    'website': "",
    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'tq_digital_videos'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/lead_generation_sequence.xml',
        'views/lead_generation.xml',
        'views/lead_generation_lines.xml',
        'wizard/lead_generation_wiz.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}