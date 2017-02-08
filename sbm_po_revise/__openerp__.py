{
	"name": "Purchase Order Revise",
	"version": "1.0",
	"depends": ["base","purchase","hr","product","sbm_purchase","sbm_purchaseorder","account","ad_purchase_import","purchase_partial_invoicing","sbm_invoice_main_currency"],
	"author": "Suprabakti Mandiri",
	"category": "Purchase Order",
	"description": """Modul ini digunakan untuk Menghandel Purchase order Revisi atau Pengganti""",
	"init_xml": [],
	'update_xml': ["po_revise.xml","search.xml"],
	'demo_xml': [],
	'installable': True,
	'active': False,
	'certificate': '',
}