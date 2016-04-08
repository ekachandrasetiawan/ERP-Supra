from openerp.report import report_sxw

class sale_order_webkit(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(sale_order_webkit, self).__init__(cr, uid, name, context=context)
