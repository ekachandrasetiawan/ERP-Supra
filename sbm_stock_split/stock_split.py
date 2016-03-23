import time
from openerp import netsvc
from datetime import date, timedelta, datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.exceptions


class product_product(osv.osv):
	_inherit = "product.product"
	_columns = {
		'split_product_ids': fields.one2many('product.split','item_to_split', string='Split Product'),
	}

product_product()

class product_split(osv.osv):
	_name = "product.split"
	_columns = {
		'item_to_split':fields.many2one('product.product',string="Product", required=True, ondelete='restrict'),
		'name':fields.related('item_to_split','name_template', type='char', string='Name'),
		'item_splited_to':fields.many2one('product.product',string="Item To Split", required=True, ondelete='restrict'),
		'result_qty_fix':fields.boolean(string='Qty Splited Basen On Result After Processing'),
		'split_into_batch':fields.boolean(string='Is Must Splited Into Batch No'),
		'state': fields.selection([
			('draft', 'Draft'),
			('active','Active'),
			('inactive','Inactive'),
			], 'Status', readonly=True, select=True, track_visibility='onchange'),
	}

	_rec_name = 'name'

	_defaults = {
		'state': 'draft',
		}

product_split()



class stock_split(osv.osv):

	def _getStockSplitNo(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			if item.state == 'draft':
				StockSplitNo = '/'
			else:
				use = str(self.pool.get('res.users').browse(cr, uid, uid).initial)
				rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
				vals = self.pool.get('ir.sequence').get(cr, uid, 'stock.split').split('/')
				StockSplitNo = time.strftime('%y')+item.no+'A/SBM-'+item.location_id.code+'-ADM/-'+use+'/'+rom[int(vals[2])]+'/'+time.strftime('%y')
			res[item.id] = StockSplitNo
		return res

	_name = "stock.split"
	_columns = {
		'stock_split_no': fields.function(_getStockSplitNo,method=True,string="Request No",type="char",
			store={
				'stock.split': (lambda self, cr, uid, ids, c={}: ids, ['location'], 20),
				'stock.split': (lambda self, cr, uid, ids, c={}: ids, ['state'], 20),
			}),
		'no':fields.char(string='No', required=True),
		'notes':fields.text(string='Notes'),
		'date_order':fields.date(string='Date Order'),
		'date_done':fields.date(string='Date Done'),
		'picking_id':fields.many2one('stock.picking', string='Stock Picking'),
		'item_output':fields.one2many('stock.split.item','stock_split_id', string='Item Output'),
		'location':fields.many2one('stock.location',required=True, string='location'),
		'state': fields.selection([
			('draft', 'Draft'),
			('submited','Submited'),
			('approved','Approved'),
			('processed','Processed'),
			('done','Done'),
			], 'Status', readonly=True, select=True, track_visibility='onchange'),	
	}

	_inherit = ['mail.thread']
	_track = {
		'state':{
			'stock_split.stock_split_submited': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'submited',
			'stock_split.stock_split_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved',
			'stock_split.stock_split_processed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'processed',
			'stock_split.stock_split_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
			'stock_split.stock_split_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
		},
	}
	_rec_name = 'no'

	_defaults = {
		'state': 'draft',
		'no':'/',
		'date_order':time.strftime('%Y-%m-%d'),
		}


	def set_request_no(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]

		stock_split = self.pool.get('stock.split')
		seq_no = self.pool.get('ir.sequence').get(cr, uid, 'stock.split')

		return stock_split.write(cr,uid,val.id,{'no':seq_no})


	def set_draft(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'draft'})
		return res

	def set_submited(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'submited'})
		return res

	def set_approved(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'approved'})
		return res

	def set_processed(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'processed'})
		return res

	def set_done(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'done'})
		return res


	def stock_split_submited(self, cr, uid, ids, context=None):


		return True

	def stock_split_approved(self, cr, uid, ids, context=None):


		return True

	def stock_split_processed(self, cr, uid, ids, context=None):


		return True

	def stock_split_validate(self, cr, uid, ids, context=None):


		return True


stock_split()


class stock_split_item(osv.osv):
	_name = "stock.split.item"
	_columns = {
		'stock_split_id':fields.many2one('stock.split',string='Stock Split'),
		'product_split_id':fields.many2one('product.split',string='Split', required=True),
		'qty':fields.float(string='Qty'),
		'uom_id':fields.many2one('product.uom',string='UOM', required=True),
		'convert_type':fields.selection([('tochange','To Change'),('tomake','To Make')], string='Convert Type'),
		'notes':fields.text('Notes'),
		'prodlot_id':fields.many2one('stock.production.lot', string='Batch No'),
		'child_ids':fields.one2many('stock.split.item.output','parent_id',string='Input'),
		'item_to_split_id':fields.related('product.split','item_to_split', type='many2one', store=False, string='Item Split'),
		'move_id':fields.many2one('stock.move', string='Move'),
		'qty_on_results':fields.boolean('Qty On Result'),

	}

	_rec_name = 'stock_split_id'

stock_split_item()


class stock_split_item_output(osv.osv):
	_name = "stock.split.item.output"
	_inherit = "stock.split.item"
	_table = "stock_split_item"
	_description = "Stock Split Item Output"
	_columns = {
		'parent_id':fields.many2one('stock.split.item', string='Parent'),
		'item_splited_to_id':fields.related('product.split','item_splited_to', type='many2one', store=False, string='Product Split'),
	}

stock_split_item_output()


