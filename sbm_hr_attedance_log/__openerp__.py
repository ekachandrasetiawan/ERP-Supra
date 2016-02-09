{
    "name": "Sbm hr Attedance Log",
    "version": "1.0",
    "depends": [
       "sbm_hr_attendance",
        "web"
        
    ],
    "author": "Suprabakti Mandiri",
    "category": "Hr attendance Log",
    "description": """Tambah acces rule , rename menu""",
 
    'data':[
        'security/ir.model.access.csv',
        ],
    
    'update_xml': [
    	'attedance_log.xml'
        
     
    ],
    
    'installable': True,
    'active': False,
    
}
