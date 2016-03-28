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
		'item_splited_to':fields.many2one('product.product',string="Item Splited To", required=True, ondelete='restrict'),
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

	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		reads = self.read(cr, uid, ids, ['name','item_to_split','item_splited_to'], context=context)
		res = []
		for record in reads:
			name = record['item_to_split'][1] + ' -----To----- ' + record['item_splited_to'][1]
			res.append((record['id'],name ))
		return res

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
				StockSplitNo = item.location.code+'/WHS/SPL'+time.strftime('%y')+'/'+item.no
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
			('cancel','Cancel'),
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
			'stock_split.stock_split_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
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

	def set_cancel(self, cr, uid, ids, context=None):
		res = self.write(cr, uid, ids, {'state': 'cancel'})
		return res

	def stock_split_set_draft(self, cr, uid, ids, context=None):
		self.set_draft(cr, uid, ids, context=None)
		return True

	def stock_split_cancel(self, cr, uid, ids, context=None):
		self.set_cancel(cr, uid, ids, context=None)
		return True

	def stock_split_submited(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]

		if val.no==False:
			self.set_request_no(cr, uid, ids, context=None)

		self.set_submited(cr, uid, ids, context=None)
		return True

	def stock_split_approved(self, cr, uid, ids, context=None):
		self.set_approved(cr, uid, ids, context=None)
		return True

	def stock_split_processed(self, cr, uid, ids, context=None):
		picking = self.create_picking(cr, uid, ids, context=None)
		self.set_processed(cr, uid, ids, context=None)
		if picking:
			self.write(cr,uid,ids,{'picking_id':picking},context=None)
		return True

	def validasi(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		for x in val.item_output:
			if x.qty==0:
				raise openerp.exceptions.Warning("Line Qty Tidak Boleh 0")
			for y in x.child_ids:
				if y.qty==0:
					raise openerp.exceptions.Warning("Child Qty Tidak Boleh 0")
		return True

	def stock_split_validate(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		stock_picking = self.pool.get('stock.picking')
		# Cek Validasi
		validasi = self.validasi(cr, uid, ids, context=None)

		if validasi==True:
			picking = stock_picking.action_move(cr, uid, [val.picking_id.id])
			if picking:
				self.set_done(cr, uid, ids, context=None)

		return True

	def create_picking(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]

		stock_picking = self.pool.get('stock.picking')
		stock_location = self.pool.get('stock.location')
		stock_move = self.pool.get('stock.move')
		work_order = self.pool.get('sbm.work.order')
		work_order_line = self.pool.get('sbm.work.order.output')

		picking_type = 'internal'
		seq_obj_name =  'stock.picking.' + picking_type

		set_loc_in = stock_location.search(cr, uid, [('name','=', 'POTONGAN IN')])
		set_loc_out = stock_location.search(cr, uid, [('name','=', 'POTONGAN OUT')])
		
		loc_id_in = stock_location.browse(cr, uid, ids, set_loc_in)[0].id
		loc_id_out = stock_location.browse(cr, uid, ids, set_loc_out)[0].id

		origin = val.stock_split_no

		# Create Stock Picking 
		picking = stock_picking.create(cr, uid, {
					# 'name':self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
					'name':'INT/SP/'+val.no,
					'origin':origin,
					'stock_journal_id':1,
					'move_type':'direct',
					'invoice_state':'none',
					'auto_picking':False,
					'type':picking_type,
					'state':'draft'
					})

		# Create Stock Move
		for line in val.item_output:
			move_id = stock_move.create(cr,uid,{
				'name' : line.product_split_id.name,
				'origin':origin,
				'product_uos_qty':line.qty,
				'product_uom':line.uom_id.id,
				'product_qty':line.qty,
				'product_uos':line.uom_id.id,
				'product_id':line.item_to_split_id.id,
				'auto_validate':False,
				'location_id' :val.location.id,
				'company_id':1,
				'picking_id': picking,
				'state':'draft',
				'location_dest_id' :47
				},context=context)

			# Create Move By Child
			for child in line.child_ids:
				move_id = stock_move.create(cr,uid,{
					'name' : line.product_split_id.name,
					'origin':origin,
					'product_uos_qty':child.qty,
					'product_uom':child.uom_id.id,
					'product_qty':child.qty,
					'product_uos':child.uom_id.id,
					'product_id':child.item_splited_to_id.id,
					'auto_validate':False,
					'location_id' :48,
					'company_id':1,
					'picking_id': picking,
					'state':'draft',
					'location_dest_id' :val.location.id
				},context=context)
				# Update Move ID Child
				self.update_split_item(cr, uid, ids, picking, move_id, child.id, context=None)

			# Update Move ID By Line
			self.update_split_item(cr, uid, ids, picking, move_id, line.id, context=None)

		stock_picking.action_assign(cr, uid, [picking])

		return picking


	def update_split_item(self, cr, uid, ids, picking, move, output_id, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		output_picking = self.pool.get('stock.split.item')
		res = output_picking.write(cr,uid,output_id,{'move_id':move},context=context)
		return res


	def print_stock_split(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"stock-split/print&id="+str(ids[0])+"&uid="+str(uid)
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'print.stock.split',
			'params': {
				'redir'	: urlTo,
				'uid':uid
			},
		}


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
		'item_to_split_id':fields.related('product_split_id','item_to_split', type='many2one', relation='product.product', store=False, string='Item Split'),
		'move_id':fields.many2one('stock.move', string='Move'),
		'qty_on_results':fields.boolean('Qty On Result'),

	}

	_rec_name = 'stock_split_id'

	def cek_product_split(self, cr, uid, ids, product_split_id, context=None):
		res = {}
		line = []
		obj_product_split = self.pool.get('product.split')
		obj_product = self.pool.get('product.product')

		product_split = obj_product_split.browse(cr, uid, product_split_id)
		product = obj_product.browse(cr, uid, product_split.item_to_split.id)

		res['uom_id'] = product.uom_id.id
		res['qty_on_results'] = product_split.result_qty_fix

		for x in product.split_product_ids:
			line.append((0,0,{
				'product_split_id':product_split_id,
				'item_to_split_id':x.item_to_split.id,
				'item_splited_to_id':x.item_splited_to.id,
				'qty': 0,
				'uom_id': x.item_splited_to.uom_id.id
				}))

		res['child_ids'] = line

		return {'value': res}

stock_split_item()


class stock_split_item_output(osv.osv):
	_name = "stock.split.item.output"
	_inherit = "stock.split.item"
	_table = "stock_split_item"
	_description = "Stock Split Item Output"
	_columns = {
		'parent_id':fields.many2one('stock.split.item', string='Parent'),
		'item_splited_to_id':fields.related('product_split_id','item_splited_to', type='many2one', relation='product.product', store=False, string='Product Split'),
	}

stock_split_item_output()



