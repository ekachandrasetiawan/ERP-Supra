{
    "name": "Account Invoice Cancel",
    "version": "1.0",
    "depends": [
        "sbm_cancel_stage",
        "account",
        "web"
        
    ],
    "author": "Suprabakti Mandiri",
    "category": "sbm setting",
    "description": """modul sbm cancel""",
 
    # 'data':[
    #     'data/religion.xml'
    # ],
    
    'update_xml': [
        "wizard_account_invoice_cancel.xml",
        "account_invoice_cancel.xml"
     
    ],
    
    'installable': True,
    'active': False,
    
}
