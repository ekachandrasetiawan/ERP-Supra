{
    "name": "Purchase Order Revise",
    "version": "1.0",
    "depends": [
                "base",
                "purchase",
                "hr",
                "product",
                "account",
                "purchase_partial_invoicing",
                "ad_purchase_import",
                "sbm_inherit",
                "sbm_purchaseorder"
                ],
    "author": "Suprabakti Mandiri",
    "category": "Purchase Order",
    "description": """Modul ini digunakan untuk Menghandel Purchase order Revisi atau Pengganti""",
    "init_xml": [],
    'update_xml': ["setting.xml","po_revise.xml"],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'certificate': '',
}