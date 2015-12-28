{
    "name": "Account Invoice Tax",
    "version": "1.0",
    "depends": [
        "sbm_e_tax_period",
        "account",
        'ad_account_finance',
        "web"
        
    ],
    "author": "Suprabakti Mandiri",
    "category": "sbm setting",
    "description": """modul sbm cancel""",
 
    # 'data':[
    #     'data/religion.xml'
    # ],
    
    'update_xml': [
    	'account_invoice.xml'
        
     
    ],
    
    'installable': True,
    'active': False,
    
}
