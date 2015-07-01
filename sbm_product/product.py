import calendar
from openerp import netsvc
from datetime import date, timedelta, datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _


class product_product(osv.osv):
	_inherit = "product.product"
	_columns = {
		'default_code' : fields.char('Part Number', size=64, select=True, required=True),
	}

	def code_change(self, cr, uid, ids, code):
		cekspace=code.replace(" ", "")
		return {'value': {'default_code': cekspace}}

	def create(self, cr, uid, vals, context=None):
		if vals['default_code']:
			cek=self.pool.get('product.product').search(cr,uid,[('default_code', '=' ,vals['default_code'])])
			if cek:
				raise osv.except_osv(('Perhatian..!!'), ('Part Number Unique ..'))
		return super(product_product, self).create(cr, uid, vals, context=context)

	# def write(self,cr,uid,ids,vals,context={}):
	# 	cek=self.pool.get('product.product').search(cr,uid,[('id', '=' ,ids)])
	# 	hasil=self.pool.get('product.product').browse(cr,uid,cek)[0]
	# 	if vals['default_code']:
	# 		cek=self.pool.get('product.product').search(cr,uid,[('default_code', '=' ,vals['default_code'])])
	# 		if cek:
	# 			raise osv.except_osv(('Perhatian..!!'), ('Part Number Unique ..'))
	# 	return super(product_product, self).write(cr, uid, ids, vals, context=context)


	def exportCSV(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]

		val = self.browse(cr, uid, ids)[0]
		idproduct=str(val.id)
		print '=====================================',idproduct
		urlTo = str(browseConf.value)+"product-product/export-csv&id="+idproduct

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

	def export_product_csv(self,cr,uid,ids,context=None):
		if context is None:
			context = {}
		idsToConfirm = context['active_ids']

		lineProduct = []
		for dataProduct in self.browse(cr,uid,idsToConfirm,context):
			line = self.pool.get('product.product').browse(cr,uid,dataProduct.id,context)
			lineProduct+=[line.id]

		print lineProduct

		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"product-product/export-csv-tree&id="+','.join(map(str,idsToConfirm))
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

product_product()