from openerp.report import report_sxw

class quotation_webkit(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(quotation_webkit, self).__init__(cr, uid, name, context=context)
