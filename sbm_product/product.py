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

	def write(self,cr,uid,ids,vals,context={}):
		cek=self.pool.get('product.product').search(cr,uid,[('id', '=' ,ids)])
		hasil=self.pool.get('product.product').browse(cr,uid,cek)[0]
		if vals['default_code']:
			cek=self.pool.get('product.product').search(cr,uid,[('default_code', '=' ,vals['default_code'])])
			if cek:
				raise osv.except_osv(('Perhatian..!!'), ('Part Number Unique ..'))
		return super(product_product, self).write(cr, uid, ids, vals, context=context)

product_product()