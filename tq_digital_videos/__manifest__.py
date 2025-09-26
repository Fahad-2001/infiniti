{
    'name': "Digital Videos",

    'summary': """
        Enhanced Project/Task Features in Community""",
    'author': "Fahad Rizwan",
    'website': "",
    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [ 'project', 'mail', 'calendar'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/task_sequence.xml',
        'data/digital_assets_sequence.xml',
        'views/project_task.xml',
        'views/digital_videos.xml',
        'views/media_type.xml',
        'views/agency.xml',
        'views/task_template.xml',
        'views/task_type.xml',
        'views/project_platform.xml',
        'views/project_project.xml',
        'views/calendar_event.xml',
        'views/calendar_status.xml',
        'views/user_access_role_view.xml',
        'wizard/digital_videos_wiz.xml',
        'wizard/mass_update_stage.xml'
    ],
}