{
    "name": "Suprabakti Mandiri Employee Add On",
    "version": "1.0",
    "depends": [
        "hr",
    ],
    "author": "IT Dev Team @ Suprabakti Mandiri",
    "category": "Human Resource",
    "description": """
        This Module is extended from HR OpenERP core for fullfill the Employee data strucuture needs in Suprabakti Mandiri
    """,
    "init_xml": [], 
    # 'demo':True,
    # 'data':[
    #     'data/religion.xml'
    # ],
    'update_xml': [
        # "rules.xml",
        # "actions.xml",
        "views.xml",
        # "menus.xml",
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    # 'js':['static/src/js/account_invoice.js'],
}