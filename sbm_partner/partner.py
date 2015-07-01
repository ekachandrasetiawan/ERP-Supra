import calendar
from openerp import netsvc
from datetime import date, timedelta, datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _

class Partner(osv.osv):
	_inherit = "res.partner"


	def exportCSV(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]

		val = self.browse(cr, uid, ids)[0]
		idpartner=str(val.id)
		print '=====================================',idpartner
		urlTo = str(browseConf.value)+"res-partner/export-csv&id="+idpartner

		return {
			'type'  : 'ir.actions.client',
			'target': 'new',
			'tag'   : 'print.out.exportcsv',
			'params': {
				# 'id'  : ids[0],
				'redir' : urlTo,
				'uid':uid
			},
		}

	def export_partner_csv(self,cr,uid,ids,context=None):
		if context is None:
			context = {}
		idsToConfirm = context['active_ids']

		lineProduct = []
		for dataProduct in self.browse(cr,uid,idsToConfirm,context):
			line = self.pool.get('res.partner').browse(cr,uid,dataProduct.id,context)
			lineProduct+=[line.id]

		print lineProduct

		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"res-partner/export-csv-tree&id="+','.join(map(str,idsToConfirm))
		print '==============url============',urlTo
		return {
			'type'  : 'ir.actions.client',
			'target': 'new',
			'tag'   : 'print.out.exportcsv',
			'params': {
				# 'id'  : ids[0],
				'redir' : urlTo,
				'uid':uid
			},
		}

Partner()
