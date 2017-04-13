import calendar
from openerp import netsvc
from datetime import date, timedelta, datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
import re

class product_product(osv.osv):
	_inherit = "product.product"

	_columns = {
		'default_code' : fields.char('Part Number', size=64, select=True, required=True),
		'product_by_location': fields.one2many('stock.product.by.location','product_id'),
	}

	def name_get(self, cr, user, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
		if not len(ids):
			return []
		def _name_get(d):
			name = d.get('name','')
			code = d.get('default_code',False)
			partner_code = d.get('partner_code','')
			if code:
				name = '[%s] %s' % (code, name)
			if d.get('variants'):
				name = name + ' - %s' % (d['variants'],)
			return (d['id'], name)

		partner_id = context.get('partner_id', False)

		result = []
		for product in self.browse(cr, user, ids, context=context):
			sellers = filter(lambda x: x.name.id == partner_id, product.seller_ids)
			if sellers:
				for s in sellers:
					mydict = {
							  'id': product.id,
							  'name': s.product_name or product.name,
							  'default_code': s.product_code or product.default_code,
							  'partner_code': s.partner_code or product.partner_code,
							  'variants': product.variants
							  }
					result.append(_name_get(mydict))
			else:
				mydict = {
						  'id': product.id,
						  'name': product.name,
						  'default_code': product.default_code,
						  'partner_code': product.partner_code,
						  'variants': product.variants
						  }
				result.append(_name_get(mydict))
		return result

	def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		if name:
			ids = self.search(cr, user, [('default_code','=',name)]+ args, limit=limit, context=context)
			if not ids:
				ids = self.search(cr, user, [('ean13','=',name)]+ args, limit=limit, context=context)
			if not ids:
				ids = self.search(cr, user, [('partner_code',operator,name)]+ args, limit=limit, context=context)
			if not ids:
				ids = set()
				ids.update(self.search(cr, user, args + [('default_code',operator,name)], limit=limit, context=context))
				if not limit or len(ids) < limit:
					ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
				if not limit or len(ids) < limit:
					ids.update(self.search(cr, user, args + [('partner_code',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
				ids = list(ids)
			if not ids:
				ptrn = re.compile('(\[(.*?)\])')
				res = ptrn.search(name)
				if res:
					ids = self.search(cr, user, [('default_code','=', res.group(2))] + args, limit=limit, context=context)
		else:
			ids = self.search(cr, user, args, limit=limit, context=context)
		result = self.name_get(cr, user, ids, context=context)
		return result
		
	def disable_product(self,cr,uid,ids,context={}):
		return self.write(cr,uid,ids,{'active':False},context=context)

	def enable_product(self,cr,uid,ids,context={}):
		return self.write(cr,uid,ids,{'active':True},context=context)

	def code_change(self, cr, uid, ids, code):
		pure_code=re.sub(r'\W+', '', code)
		# replace non alphanumeric characters
		return {'value': {'default_code': pure_code}}

	def create(self, cr, uid, vals, context=None):
		if vals['default_code']:
			cek=self.pool.get('product.product').search(cr,uid,[('default_code', '=' ,vals['default_code'])])
			if cek:
				raise osv.except_osv(('Perhatian..!!'), ('Part Number Unique ..'))
		return super(product_product, self).create(cr, uid, vals, context=context)

	def exportCSV(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]

		val = self.browse(cr, uid, ids)[0]
		idproduct=str(val.id)
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


	def action_cek_stock_loc(self,cr,uid,ids,context=None):
		if context is None:
			context = {}
		
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_product', 'wizard_stock_by_location')

		context.update({
			'active_model': self._name,
			'active_ids': ids,
			'active_id': len(ids) and ids[0] or False
		})
		return {
			'view_mode': 'form',
			'view_id': view_id,
			'view_type': 'form',
			'view_name':'wizard_stock_by_location',
			'res_model': 'wizard.stock.by.location',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
			'nodestroy': True,
		}

product_product()


class WizardStockByLocation(osv.osv_memory):

	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		product_ids = context.get('active_ids', [])
		active_model = context.get('active_model')

		res = super(WizardStockByLocation, self).default_get(cr, uid, fields, context=context)
		product_id, = product_ids
		if product_id:
			res.update(product_id=product_id)

			linesData = []
			loc = self.pool.get('stock.location').search(cr, uid, [('usage', '=',['inventory','internal'])])
			for x in self.pool.get('stock.location').browse(cr, uid, loc):
				if not context:
					context = {}
				context['location'] = x.id
				product =self.pool.get('product.product').browse(cr, uid, product_id, context=context)

				# Menampilkan Location SITE saja
				if x.location_id.id == 49:
					linesData.append({
						'location_id' : x.id,
						'qty_available':product.qty_available,
						'virtual_available':product.virtual_available,
						'incoming_qty':product.incoming_qty,
						'outgoing_qty':product.outgoing_qty,
					})

			res.update(lines=linesData)
		return res


	_name="wizard.stock.by.location"
	_description="Wizard Stock By Location"
	_columns = {
		'product_id':fields.many2one('product.product',string="Product"),
		'lines':fields.one2many('wizard.stock.by.location.line','w_id',string="Lines", readonly=True),
	}
	_rec_name="product_id"


WizardStockByLocation()


class WizardWizardStockByLocLine(osv.osv_memory):

	_name="wizard.stock.by.location.line"

	_description="Line Wizard Cancel Item On P.O"
	_columns={
		'w_id':fields.many2one('wizard.stock.by.location',string="Wizard",required=True,ondelete='CASCADE',onupdate='CASCADE'),
		'location_id':fields.many2one('stock.location','Product Location'),
		'product_id':fields.many2one('product.product','Product'),
		'qty_available': fields.float(string='On Hand'),
		'virtual_available': fields.float(string='Forecasted Qty'),
		'incoming_qty': fields.float(string='Incoming'),
		'outgoing_qty': fields.float(string='Outgoing'), 
	}
	_rec_name = 'w_id'

WizardWizardStockByLocLine()