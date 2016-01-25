{
    "name": "new sbm sale order",
    "version": "1.0",
    "depends": [
        "sale",
        "sbm_inherit",
        'ad_delivery_note',
        "web"

        
    ],
    "author": "Suprabakti Mandiri",
    "category": "Sales Suprabakti",
    "description": """sale order baru""",
 
    # 'data':[
       
    # ],
    'data':[
        'security/ir.model.access.csv',
        'security_rmpsm/ir.model.access.csv',
    ],
    
    'update_xml': [
        
        "win_quatition_wizard.xml",
        "wizard_revised_quotation.xml",
        "wizard_lost_quotation.xml",
        "sbm_quotation.xml",
        # "reportview.xml",
        "file.sql"
       
    ],
    
    'installable': True,
    'active': False,
    
    
}
