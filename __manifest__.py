{
    'name': 'website_bensizwe',
    'version': '2.0',
    'summary': 'Custom website module for Bensizwe with modern user space',
    'description': '''
    This module provides custom website functionalities for Bensizwe including:
    - Modern user space with timeline, cards, and responsive design
    - Enhanced profile management with avatar support
    - Improved candidate experience with statistics and navigation
    - Advanced form validation and user interactions
    - Modern CSS animations and responsive design
    ''',
    'author': 'Bensizwe Development Team',
    'website': 'http://www.bensizwe.com',
    'category': 'Website',
    'depends': ['website', 'website_hr_recruitment', 'hr', 'website_blog', 'portal', 'mail'],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_applicant_views.xml",
        "views/snippets/options.xml",
        "views/snippets/s_rows_jobs_out_.xml",
        "views/snippets/s_rows_jobs.xml",
        "views/website_training_template.xml",
        "views/website_training_views.xml",
        "views/website_user_views.xml",
        "views/website_training_validation_template.xml",
        "views/candidat_auth_templates.xml",
        "views/candidat_mon_espace_template.xml",
        "views/hr_job_form_inherit_extra_fields.xml",
        "views/website_job_detail_template.xml",
        "views/forms/website_form_formation.xml",
        "views/forms/ajout_experience_education_langage_templates.xml",
        "views/report_cv_pdf_template.xml",
        "views/snippets/snippet3collones_dynamic.xml",
        "views/website_blog_bensizwe.xml",
        "views/formation_registration_templates.xml",
        "views/portal_formations.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            # Images et icônes
            'website_bensizwe/static/src/img/*',
            'website_bensizwe/static/src/img/icons/*.svg',
            
            # Styles CSS/SCSS
            'website_bensizwe/static/src/scss/website_bensizwe.scss',
            'website_bensizwe/static/src/scss/profile_modal.scss',
            
            # JavaScript pour l'interactivité
            'website_bensizwe/static/src/js/*.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': [],
    },
    'demo': [],
    'test': [],
    'pre_init_hook': None,
    'post_init_hook': None,
    'uninstall_hook': None,
}