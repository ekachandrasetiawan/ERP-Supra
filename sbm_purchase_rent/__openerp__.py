{
    "name": "Purchase Requisition Rent Suprabakti",
    "version": "1.0",
    "depends": ["sbm_purchase","hr","product","ad_npwp_partner","web","sbm_purchase"],
    "author": "Suprabakti Mandiri",
    "category": "Purchase Suprabakti",
    "description": """Modul ini digunakan untuk Menggolah Data Purchase Barang Rental""",
    "init_xml": [],
    'update_xml': [
        "purchase_rent.xml",
        "rent_items.xml",
        "rent_requisition_detail.xml",
        # "contract.xml",
        # "contract_detail.xml",
        "term/term_payment.xml",
        # "contract/po_contract.xml"
        "menu.xml",
    ],
    'js' : ['static/js/rent.js'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}