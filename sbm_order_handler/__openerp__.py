{
	'name' : 'SBM ORDER HANDLER',
	'version' : '1.1',
	'author' : 'PT.SUPRABAKTI MANDIRI',
	'category' : 'ORDER',
	'description' : """ ALL SBM ORDER HANDLER """,
	'depends': [
		'sale',
		'sbm_saleorder',
		'sbm_inherit',
		'ad_delivery_note',
		'web',
		'base',
		'stock',
		'ad_order_preparation',
		'mail',
		'product',
		'mrp',
		'account',
		'purchase',
		'sbm_purchase',
		'sbm_purchaseorder',
		'sbm_e_tax_period',
		'ad_account_finance',
		],
	'data': [
		'new_sbm_sale_order/file.sql',
		'new_sbm_sale_order/security/ir.model.access.csv',
		'new_sbm_sale_order/security_rmpsm/ir.model.access.csv',
	],
	'update_xml': [
		'new_sbm_sale_order/sbm_quotation.xml',
		'new_sbm_sale_order/win_quatition_wizard.xml',
		'new_sbm_sale_order/wizard_lost_quotation.xml',
		'new_sbm_sale_order/wizard_revised_quotation.xml',
		'new_sbm_sale_order/print_name_button.xml',
		'new_sbm_sale_order/wizardcreatepb.xml',
		'sbm_order_preparation/setting.xml',
		'sbm_order_preparation/sbm_order_preparation_view.xml',
		'sbm_order_preparation/search.xml',
		'sbm_delivery_note/setting.xml',
		'sbm_delivery_note/sbm_delivery_note_view.xml',
		'sbm_delivery_note/search.xml',
		'sbm_delivery_note/support/support.xml',
		'sbm_work_order/setting.xml',
		'sbm_work_order/work_order_view.xml',
		'sbm_work_order/adhoc_order_request_view.xml',
		'sbm_stock_split/stock_split_view.xml',
		'sbm_stock_split/search.xml',
		'sbm_stock_split/setting.xml',
		'sbm_cancel_stage/sbmcancel.xml',
		'sbm_account_invoice_cancel/wizard_account_invoice_cancel.xml',
		'sbm_account_invoice_cancel/account_invoice_cancel.xml',
		'sbm_invoice_multi_po/invoice_multi_po_view.xml',
		'sbm_e_faktur/account_invoice.xml',
	],
	'js': [
		'sbm_delivery_note/static/src/js/delivery_note.js',
		'sbm_work_order/static/src/js/work_order.js',
		'sbm_stock_split/static/src/js/stock_split.js',
	],
	'demo_xml': [],
	'installable': True,
	'auto_install': False,
	'certificate': '',
}
