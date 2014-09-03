{
    "name": "ADSOFT",
    "version": "1.0",
    "depends": ["sale","ad_delivery_note", "account", "report_webkit"],
    "author": "Adsoft",
    "category": "Custom Supra/ Sales Admin Report",
    "description": """
    This module provide :
    Create Purchase Order Form
    
    Added :
        - Blank Line
    
    Wekit Setting:
        - /usr/local/bin/wkhtmltopdf
    """,
    "init_xml": [],
    'update_xml': [
                   "dn/data_dn.xml",
                   "pl/data_pl.xml",
                   "do/data_do.xml",
                   "spk/data_spk.xml",
                   "pl/pl_view.xml",
                   "report_view.xml",
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
