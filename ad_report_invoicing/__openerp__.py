{
    "name": "Report Invoicing",
    "version": "1.0",
    "depends": ["account", "report_webkit"],
    "author": "Adsoft",
    "category": "Custom Supra/ Invoicing Report",
    "description": """
    This module provide :
    - Print-Out for Customer Invoice
    - Print-Out for Tax Invoice
    - Print-Out for Kwitansi
    
    Wekit Setting:
        - /usr/local/bin/wkhtmltopdf
    """,
    "init_xml": [],
    'update_xml': [
                   "inv/data_inv.xml",
                   "report_view.xml",
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
