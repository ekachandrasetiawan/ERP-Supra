import calendar
from openerp import netsvc
from datetime import date, timedelta, datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _

class product_product(osv.osv):
	_inherit = "product.product"

	_columns = {
		'default_code' : fields.char('Part Number', size=64, select=True, required=True),
		'product_by_location': fields.one2many('stock.product.by.location','product_id'),
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

				

				if product.qty_available <> 0.0:
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
		'virtual_available': fields.float(string='Available'),
		'incoming_qty': fields.float(string='Incoming'),
		'outgoing_qty': fields.float(string='Outgoing'), 
	}
	_rec_name = 'w_id'

WizardWizardStockByLocLine()