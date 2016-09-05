{
    "name": "Purchase Suprabakti",
    "version": "1.0",
    "depends": [
                "purchase",
                "hr",
                "product",
                "sale",
                "sbm_saleorder"
                ],
    "author": "Suprabakti Mandiri",
    "category": "Purchase Suprabakti",
    "description": """Modul ini digunakan untuk Menggolah Data Purchase""",
    "init_xml": [],
    # 'update_xml': ["view_purchase.xml","menu.xml","setting.xml","search.xml"],
    'demo_xml': [],
    'data': [
        'wizard/purchase_requisition_form_view.xml',
        'view_purchase.xml',
        'setting.xml',
        'menu.xml',
        'search.xml',
    ],
    'installable': True,
    'active': False,
}