{
	"name": "E-Faktur Support Module",
	"version": "1.0",
	"depends": [
		"web",
		"hr",
		"account",
		"product",
		"sbm_account_invoice_line_tax_amount"
	],
	"author": "IT Dev Team @ Suprabakti Mandiri",
	"category": "Account",
	"description": """
		Untuk memenuhi kebutuhan integerasi dengan program E-Fakttur Direktorat Jendral Pajak
		Isi : 
			- Modul Export data invoice, customer, barang.
			- Modul pengecekan customer dan barang baru yang belum di export ke sistem E-Faktur
	""",
	"init_xml": [], 
	# 'demo':True,
	# 'data':[
	#     'data/religion.xml'
	# ],
	'update_xml': [
		# "rules.xml",
		# "actions.xml",
		"view_export.xml",
		# "menus.xml",
	],
	'demo_xml': [],
	'installable': True,
	'active': False,
	# 'js': ['static/src/js/resource.js'],
	# 'qweb': ['static/src/xml/resource.xml'], 
	# 'js':['static/src/js/account_invoice.js'],
}