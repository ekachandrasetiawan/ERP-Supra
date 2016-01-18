{
    "name": "Purchase Suprabakti",
    "version": "1.0",
    "depends": ["purchase","hr","product","sale","sbm_saleorder",'sbm_inherit','ad_delivery_note'],
    "author": "Suprabakti Mandiri",
    "category": "Purchase Suprabakti",
    "description": """Modul ini digunakan untuk Menggolah Data Purchase""",
    "init_xml": [],
    # 'update_xml': ["view_purchase.xml","menu.xml","setting.xml","search.xml"],
    'demo_xml': [],
    'data': [
        'wizard/purchase_requisition_form_view.xml',
        'view_purchase.xml',
        'menu.xml',
        'setting.xml',
        'search.xml',
    ],
    'installable': True,
    'active': False,
}