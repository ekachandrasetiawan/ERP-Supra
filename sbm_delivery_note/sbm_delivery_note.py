from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import openerp.exceptions
from lxml import etree
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from openerp.tools.float_utils import float_compare


class delivery_note(osv.osv):
	_inherit = "delivery.note"
	_columns = {
		'poc': fields.char('Customer Reference', size=64,track_visibility='onchange',readonly=True, states={'draft': [('readonly', False)]}),
		'tanggal' : fields.date('Delivery Date',track_visibility='onchange',readonly=True, states={'draft': [('readonly', False)]}),
		'attn':fields.many2one('res.partner',string="Attention",readonly=True, states={'draft': [('readonly', False)]}),
		'note_lines': fields.one2many('delivery.note.line', 'note_id', 'Note Lines', readonly=True, states={'draft': [('readonly', False)]}),
		'picking_id': fields.many2one('stock.picking', 'Stock Picking', domain=[('type', '=', 'out')], required=False,readonly=True, states={'draft': [('readonly', False)]}),
		'postpone_picking': fields.many2one('stock.picking', 'Postpone Picking', required=False,readonly=True, states={'draft': [('readonly', False)]}),
		'work_order_id': fields.many2one('perintah.kerja',string="SPK",store=True,required=False,readonly=True, states={'draft': [('readonly', False)]}),
		'work_order_in': fields.many2one('perintah.kerja.internal',string="SPK Internal",readonly=True, states={'draft': [('readonly', False)]}),
		'state': fields.selection([('draft', 'Draft'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Cancel'), ('torefund', 'To Refund'), ('refunded', 'Refunded'),('postpone', 'Postpone')], 'State', readonly=True,track_visibility='onchange'),
	}

	_order = "id desc"


	def create(self, cr, uid, vals, context=None):
		prepareExists = self.search(cr,uid,[('prepare_id','=',vals['prepare_id']),('state','not in',['cancel'])])
		if prepareExists and vals['special']==False:
			no = ""
			for nt in self.browse(cr,uid,prepareExists,context):
				no += "["+nt.name+"]\n"
			raise osv.except_osv(_("Error!!!"),_("Deliver Note ref to requested DO NO is Exist On NO "+no))
		vals['name'] ='/'


		for lines in vals['note_lines']:
			if lines[2]:
				if lines[2]['product_qty'] == 0:
					# Cek Part Number Value
					product = self.pool.get('product.product').browse(cr, uid, [lines[2]['product_id']])[0]

					raise osv.except_osv(_("Error!!!"),_("Product Qty "+ product.default_code + " Not '0'"))
		return super(delivery_note, self).create(cr, uid, vals, context=context)



	def prepare_change(self, cr, uid, ids, pre):
		res = super(delivery_note,self).prepare_change(cr, uid, ids, pre)
		if pre :
			res = {}; line = []
			

			data = self.pool.get('order.preparation').browse(cr, uid, pre)
			dnid = self.pool.get('delivery.note').search(cr, uid, [('prepare_id', '=', pre), ('state', '=', 'done')])

			product =[x.sale_line_material_id.sale_order_line_id.id for x in data.prepare_lines if x.sale_line_material_id]

			if product == []:
				raise openerp.exceptions.Warning("Order Preparation Tidak Memiliki Material Lines")

			order_line = self.pool.get('sale.order.line').search(cr, uid, [('id', 'in', product)])
			data_order_line = self.pool.get('sale.order.line').browse(cr, uid, order_line)

			qty_dn_line = 0

			for y in data_order_line:
				so_material_line = self.pool.get('sale.order.material.line').search(cr, uid, [('sale_order_line_id', '=', [y.id])])
				data_material_line = self.pool.get('sale.order.material.line').browse(cr, uid, so_material_line)					

				material_line = []

				# Cek Jumlah Line Material
				if len(data_material_line) == 1:

					for qty_dn in data_material_line:
						
						if qty_dn.product_id.id == y.product_id.id:
							op_qty = self.pool.get('order.preparation.line').search(cr, uid, [('sale_line_material_id', '=', [qty_dn.id]), ('preparation_id', '=', [pre])])
							qty_op = self.pool.get('order.preparation.line').browse(cr, uid, op_qty)[0]
							
							# Set Product Qty yang bukan Set
							qty_dn_line = qty_op.product_qty


				for dline in data_material_line:
					op_line = self.pool.get('order.preparation.line').search(cr, uid, [('sale_line_material_id', '=', [dline.id]), ('preparation_id', '=', [pre])])
					data_op_line = self.pool.get('order.preparation.line').browse(cr, uid, op_line)

					
					if data_op_line:
						for dopline in data_op_line:

							# Cek Batch
							batch = self.pool.get('order.preparation.batch').search(cr, uid, [('batch_id', '=', [dopline.id])])
							data_batch = self.pool.get('order.preparation.batch').browse(cr, uid, batch)

							if data_batch:
								# Jika Ada Batch Maka Tampilkan Batch
								for xbatch in data_batch:
									material_line.append((0,0,{
										'name':dopline.product_id.id,
										'prodlot_id':xbatch.name.id,
										'desc':xbatch.desc,
										'qty':xbatch.qty,
										'product_uom':dopline.product_uom.id,
									}))
							else:
								material_line.append((0,0,{
									'name':dopline.product_id.id,
									'desc':dopline.name,
									'qty':dopline.product_qty,
									'product_uom':dopline.product_uom.id
									}))
				line.append({
					'no': y.sequence,
					'product_id' : y.product_id.id,
					'product_qty': qty_dn_line,
					'product_uom': x.product_uom.id,
					'name': y.name,
					'note_lines_material': material_line
					})

			res['note_lines'] = line
			res['poc'] = data.sale_id.client_order_ref
			res['tanggal'] = data.duedate
			res['partner_id'] = data.sale_id.partner_id.id
			res['partner_shipping_id'] = data.sale_id.partner_shipping_id.id
			res['attn'] = data.sale_id.attention.id
		return  {'value': res}


	def package_confirm(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		dn = self.pool.get('delivery.note')
		dn_line = self.pool.get('delivery.note.line')
		dn_material = self.pool.get('delivery.note.line.material')
		stock_picking = self.pool.get('stock.picking')
		stock_move = self.pool.get('stock.move')
		

		# Create No Delivery Note
		if val.special==True:
			rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
			usa = 'SPC'
			vals = self.pool.get('ir.sequence').get(cr, uid, 'delivery.note').split('/')
			use = str(self.pool.get('res.users').browse(cr, uid, uid).initial)
			dn_no =time.strftime('%y')+ vals[-1]+'C/SBM-ADM/'+usa+'-'+use+'/'+rom[int(vals[2])]+'/'+vals[1]
		else:    
			rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
			saleid = self.pool.get('order.preparation').browse(cr, uid, val.prepare_id.id).sale_id.id
			usa = str(self.pool.get('sale.order').browse(cr, uid, saleid).user_id.initial)
			vals = self.pool.get('ir.sequence').get(cr, uid, 'delivery.note').split('/')
			use = str(self.pool.get('res.users').browse(cr, uid, uid).initial)
			dn_no =time.strftime('%y')+ vals[-1]+'C/SBM-ADM/'+usa+'-'+use+'/'+rom[int(vals[2])]+'/'+vals[1]

		picking_type = 'out'
		seq_obj_name =  'stock.picking.' + picking_type

		# Create Stock Picking 
		picking = stock_picking.create(cr, uid, {
					'name':self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
					'origin':val.prepare_id.sale_id.name,
					'partner_id':val.partner_id.id,
					'stock_journal_id':1,
					'move_type':'direct',
					'invoice_state':'none',
					'auto_picking':False,
					'type':picking_type,
					'sale_id':val.prepare_id.sale_id.id,
					'note_id':val.id,
					'state':'draft'
					})

		# Create Stock Move
		for line in val.note_lines:
			for x in line.note_lines_material:
				move_id = stock_move.create(cr,uid,{
					'name' : x.name.name,
					'origin':val.prepare_id.sale_id.name,
					'product_uos_qty':x.qty,
					'product_uom':x.product_uom.id,
					'prodlot_id':x.prodlot_id.id,
					'product_qty':x.qty,
					'product_uos':x.product_uom.id,
					'partner_id':val.partner_id.id,
					'product_id':x.name.id,
					'auto_validate':False,
					'location_id' :12,
					'company_id':1,
					'picking_id': picking,
					'state':'draft',
					'location_dest_id' :9
					},context=context)
				
				# Update DN Line Material Dengan ID Move
				dn_material.write(cr,uid,x.id,{'stock_move_id':move_id})

		
		# Update Picking id di DN
		dn.write(cr,uid,val.id,{'picking_id':picking,'name':dn_no})

		stock_picking.action_assign(cr, uid, [picking])

		res = super(delivery_note,self).package_confirm(cr, uid, ids, context=None)
		return res


	def package_draft(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		if val.postpone_picking:
			move = self.pool.get('stock.move').search(cr, uid, [('picking_id', '=', [val.postpone_picking.id])])
			data = self.pool.get('stock.move').browse(cr, uid, move)
			# Delete Move Postpone Picking
			for x in data:
				self.pool.get('stock.move').write(cr,uid,x.id,{'state':'draft'})
				self.pool.get('stock.move').unlink(cr,uid,[x.id],context)

			# Delete  Postpone Picking
			self.pool.get('stock.picking').write(cr,uid,val.postpone_picking.id,{'state':'draft'})
			self.pool.get('stock.picking').unlink(cr,uid,[val.postpone_picking.id],context)
			self.write(cr, uid, ids, {'state': 'draft','postpone_picking':False})

		if val.picking_id:
			move = self.pool.get('stock.move').search(cr, uid, [('picking_id', '=', [val.picking_id.id])])
			data = self.pool.get('stock.move').browse(cr, uid, move)
			# Delete Move Picking
			for x in data:
				self.pool.get('stock.move').write(cr,uid,x.id,{'state':'draft'})
				self.pool.get('stock.move').unlink(cr,uid,[x.id],context)

			# Delete Picking
			self.pool.get('stock.picking').unlink(cr,uid,[val.picking_id.id],context)
			self.write(cr, uid, ids, {'state': 'draft','picking_id':False})
		
		self.write(cr, uid, ids, {'state': 'draft'})
		return True                               


	def package_postpone(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		dn = self.pool.get('delivery.note')
		dn_line = self.pool.get('delivery.note.line')
		dn_material = self.pool.get('delivery.note.line.material')
		stock_picking = self.pool.get('stock.picking')
		stock_move = self.pool.get('stock.move')

		picking_type = 'out'
		seq_obj_name =  'stock.picking.' + picking_type

		if val.postpone_picking:
			stock_picking.write(cr,uid,val.postpone_picking.id,{'state':'done'})

			for move_line in val.postpone_picking.move_lines:
				stock_move.write(cr,uid,move_line.id,{'state':'done'})
		else:
			# Create Stock Picking 
			picking = stock_picking.create(cr, uid, {
						'name':self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
						'origin':val.prepare_id.sale_id.name,
						'partner_id':val.partner_id.id,
						'stock_journal_id':1,
						'move_type':'direct',
						'invoice_state':'none',
						'auto_picking':False,
						'type':picking_type,
						'sale_id':val.prepare_id.sale_id.id,
						'note_id':val.id,
						'is_postpone':True,
						'state':'done'
						})

			# Create Stock Move
			location = self.pool.get('stock.location').search(cr, uid, [('code', '=', 'PRTS')])
			data_location = self.pool.get('stock.location').browse(cr, uid, location)[0]

			for line in val.note_lines:
				for x in line.note_lines_material:
					move_id = stock_move.create(cr,uid,{
						'name' : x.name.name,
						'origin':val.prepare_id.sale_id.name,
						'product_uos_qty':x.qty,
						'product_uom':x.product_uom.id,
						'prodlot_id':x.prodlot_id.id,
						'product_qty':x.qty,
						'product_uos':x.product_uom.id,
						'partner_id':val.partner_id.id,
						'product_id':x.name.id,
						'auto_validate':False,
						'location_id' :12,
						'company_id':1,
						'picking_id': picking,
						'state':'done',
						'location_dest_id' : data_location.id
						},context=context)
					
					# Update DN Line Material Dengan ID Move
					dn_material.write(cr,uid,x.id,{'stock_move_id':move_id})

			# Update Picking id di DN
			dn.write(cr,uid,val.id,{'postpone_picking':picking})

		self.write(cr, uid, ids, {'state': 'postpone'})
		return True


	def package_continue(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		stock_picking = self.pool.get('stock.picking')
		stock_move = self.pool.get('stock.move')

		if val.postpone_picking:
			stock_picking.write(cr,uid,val.postpone_picking.id,{'state':'cancel'})

			for move_line in val.postpone_picking.move_lines:
				stock_move.write(cr,uid,move_line.id,{'state':'cancel'})

		self.write(cr, uid, ids, {'state': 'approve'})
		return True


	def package_new_validate(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		stock_picking = self.pool.get('stock.picking')
		stock_move = self.pool.get('stock.move')
		partial_data = {}
		move = self.pool.get('stock.move').search(cr, uid, [('picking_id', '=', val.picking_id.id)])
		data_move = self.pool.get('stock.move').browse(cr, uid, move)
		# Update Done Picking & Move
		stock_picking.action_move(cr, uid, [val.picking_id.id])

		self.write(cr, uid, ids, {'state': 'done'})
		return True
		

	def package_cancel(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		stock_picking = self.pool.get('stock.picking')
		stock_move = self.pool.get('stock.move')

		if val.picking_id:
			stock_picking.action_cancel(cr, uid, [val.picking_id.id])

		if val.postpone_picking:
			stock_picking.action_cancel(cr, uid, [val.postpone_picking.id])

		self.write(cr, uid, ids, {'state':'cancel'})
		return True



delivery_note()

class delivery_note_line(osv.osv):
	def _get_refunded_item(self,cr,uid,ids,field_name,arg,context={}):

		return super(delivery_note_line,self)._get_refunded_item(cr,uid,ids,field_name,arg,context={})

	_inherit = "delivery.note.line"
	_columns = {
		'no': fields.integer('No'),
		'name': fields.text('Description'),
		'note_id': fields.many2one('delivery.note', 'Delivery Note', required=True, ondelete='cascade'),
		'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)]),
		'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
		'product_uom': fields.many2one('product.uom', 'UoM'),
		'product_packaging': fields.many2one('product.packaging', 'Packaging'),
		'op_line_id':fields.many2one('order.preparation.line','OP Line',required=True),
		'note_line_return_ids': fields.many2many('stock.move','delivery_note_line_return','delivery_note_line_id',string="Note Line Returns"),
		'refunded_item': fields.function(_get_refunded_item, string='Refunded Item', store=False),
		'state': fields.selection([('torefund', 'To Refund'), ('refunded', 'Refunded'),('donerefund', 'Done Refund')], 'State', readonly=True),
		'note_lines_material': fields.one2many('delivery.note.line.material', 'note_line_id', 'Note Lines Material', readonly=False),
	}

delivery_note_line()


class delivery_note_line_material(osv.osv):
	_name = "delivery.note.line.material"
	_columns = {
		'name' : fields.many2one('product.product',required=True, string="Product"),
		'prodlot_id':fields.many2one('stock.production.lot','Serial Number'),
		'note_line_id': fields.many2one('delivery.note.line', 'Delivery Note Line', required=True, ondelete='cascade'),
		'qty': fields.float('Qty',required=True),
		'product_uom': fields.many2one('product.uom',required=True, string='UOM'),
		'stock_move_id': fields.many2one('stock.move',required=False, string='Stock Move'),
		'desc': fields.text('Description',required=False),
		'state': fields.related('note_line_id','state', type='many2one', relation='delivery.note.line', string='State'),
	}

delivery_note_line_material()


class stock_picking(osv.osv):
	_name = 'stock.picking'
	_inherit = ["stock.picking","mail.thread"]
	_columns = {
		'is_postpone': fields.boolean('Is Postpone'),
	}

stock_picking()


