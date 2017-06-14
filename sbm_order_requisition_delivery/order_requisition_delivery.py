import re
import time
import netsvc
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta

class order_requisition_delivery(osv.osv):

	def _get_pr_names(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			move=self.pool.get('order.requisition.delivery.line').search(cr,uid,[('order_requisition_delivery_id', '=' ,item.id)])
			line = [data.purchase_requisition_id.name[:5] for data in self.pool.get('order.requisition.delivery.line').browse(cr,uid,move)]
			hasil= ''
			for x in set(line):
				hasil += x + ', '
			res[item.id] = hasil
		return res


	_name = 'order.requisition.delivery'
	_columns = {
		'name':fields.char('Refference',required=True, readonly=False,size=64,states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
		'source_location': fields.many2one('stock.location', "Source Location", required=True, states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
		'destination_location_id': fields.many2one('stock.location', "Destination Location", required=True,states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
		'date':fields.date('Date',required=True,states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
		'pr_names': fields.function(_get_pr_names,string="PR Names",type="char",store=False, readonly=False,states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
		'notes':fields.text('Date',required=False,states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
		'lines': fields.one2many('order.requisition.delivery.line', 'order_requisition_delivery_id', 'Lines',readonly=False,states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
		'state': fields.selection([
			('draft', 'Draft'),
			('confirmed', 'Wait For Approve'),
			('approved', 'Ready To Transfer'),
			('done','Received'),
			],
			'State'),
		'picking_id': fields.many2one('stock.picking', "Stock Picking", required=False, readonly=True),
		'prepare_by':fields.many2one('res.users',string="Prepare",ondelete="CASCADE",onupdate='CASCADE',readonly=True),
		'confirmed_by':fields.many2one('res.users',string="Confirmed",ondelete="CASCADE",onupdate='CASCADE',readonly=True),
		'approved_by':fields.many2one('res.users',string="Approved",ondelete="CASCADE",onupdate='CASCADE',readonly=True),
		'received_by':fields.many2one('res.users',string="Received",ondelete="CASCADE",onupdate='CASCADE',readonly=True),
	}
	_inherit = ['mail.thread']
	_track = {
		'note':{},
		'state':{
			'sbm_order_requisition_delivery.ord_pack_confirm': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirmed',
			'sbm_order_requisition_delivery.ord_pack_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved',
			'sbm_order_requisition_delivery.ord_pack_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
			'sbm_order_requisition_delivery.ord_pack_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
		},
	}
	_defaults = {
		'name': '/',
		'state': 'draft',
		'date':time.strftime('%Y-%m-%d'),
	}


	def create(self, cr, uid, vals, context={}):
		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'order.requisition.delivery')

		offer_id = super(order_requisition_delivery, self).create(cr, uid, vals, context=context)
		order = self.browse(cr, uid, offer_id, context=context) or []

		lines = self.pool.get('order.requisition.delivery.line').search(cr, uid, [('order_requisition_delivery_id', '=', order.id)])

		for x in self.pool.get('order.requisition.delivery.line').browse(cr, uid, lines):
			if x.qty_delivery ==0:
				raise osv.except_osv(('Warning !!!'), ('Qty To Send Can Not "0"'))


		return offer_id

	def def_confirmed(self,cr,uid,ids,context=None):

		return self.write(cr,uid,ids,{'state':'confirmed','confirmed_by':uid})

	def def_approved(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids)[0]

		return self.write(cr,uid,ids,{'state':'approved','approved_by':uid})

	def def_validate(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids)[0]
		if val.source_location.id == val.destination_location_id.id:
			raise osv.except_osv(_('Warning!'), _('Tujuan dan Sumber Pengiriman,\n Tidak Boleh sama'))
		else:
			stock_picking = self.pool.get("stock.picking")
			stock_move = self.pool.get('stock.move')
			picking_type = 'out'
			seq_obj_name =  'stock.picking.' + picking_type
			
			picking = stock_picking.create(cr, uid, {
									'name':self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
									'origin':val.name,
									'state':'done'
									})
			for line in val.lines:
				move_id = stock_move.create(cr,uid,
					{
					'name' : self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
					'product_id': line.product_id.id,
					'product_qty': line.qty_delivery,
					'product_uom': line.uom_id.id,
					'location_id' : val.source_location.id,
					'location_dest_id' : val.destination_location_id.id,
					'picking_id': picking,
					'state':'done'
					},context=context)

				self.pool.get('order.requisition.delivery.line').write(cr, uid, line.id, {'state':'done'}, context=context)
			self.pool.get('order.requisition.delivery').write(cr, uid, ids, {'state':'done'}, context=context)

			return self.write(cr,uid,ids,{'state':'done','picking_id':picking,'received_by':uid})

	def def_draft(self,cr,uid,ids,context=None):

		return self.write(cr,uid,ids,{'state':'draft'})
	

order_requisition_delivery()


class order_requisition_delivery_line(osv.osv):

	def _get_qty_available(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			move=self.pool.get('purchase.order.line').search(cr,uid,[('line_pb_general_id', '=' ,item.id)])
			hasil= 0
			for data in  self.pool.get('purchase.order.line').browse(cr,uid,move):
				hasil += data.received_items-data.supplied_items
			res[item.id] = hasil
		return res

	_name = 'order.requisition.delivery.line'
	_columns = {
		'name': fields.many2one('product.product', "Product", required=False, select=True),
		'order_requisition_delivery_id':fields.many2one('order.requisition.delivery', 'Order Requisition Delivery', required=False, ondelete='cascade',change_default=True),
		'purchase_requisition_id':fields.many2one('pembelian.barang', 'PB No', required=False, ondelete='cascade',select=True,domain=[('state','=','purchase')]),
		'purchase_requisition_line_id': fields.many2one('detail.pb', 'Detail PB',required=False, ondelete='cascade',select=True),
		'product_id': fields.related('purchase_requisition_line_id','name', type='many2one', relation='product.product', string='Item PB'),
		'desc':fields.text('Description', required=False),
		'move_id':fields.many2one('stock.move', 'Stock Move', required=False, ondelete='cascade'),
		'qty_delivery':fields.float('Qty To Send', required=False,readonly=False),
		'qty':fields.float('Qty Items', required=False,readonly=False),
		'received_items_po': fields.float(string="Received Items", readonly=False),	
		'uom_id':fields.many2one('product.uom', 'UOM', required=False),
		'qty_available': fields.function(_get_qty_available,string="Qty Available",type="float",store=True),
		'picked_po':fields.one2many('order.requisition.delivery.line.po','order_requisition_delivery_line_id','Picking PO'),
		'notes':fields.text('Notes'),
		'state': fields.selection([
			('draft', 'Draft'),
			('confirmed', 'Confirmed'),
			('approved', 'Approved'),
			('done','Done'),
			],
			'State'),
	}
	_defaults = {
		'state': 'draft',
	}


	def cek_qty_delivery(self, cr, uid, ids, qty_available,qty_delivery, product_id,context=None):
		res = {}; line = []
		if qty_delivery > qty_available:
			warning = {"title": ("Warning"), "message": ("Product Item Delivery Tidak Mencukupi")}
			return {
					'warning': warning, 
					'value': 
						{
							'qty_delivery': 0
						}
				}
		else:
			cek=self.pool.get('purchase.order.line').search(cr,uid,[('line_pb_general_id', '=' ,product_id)])
			data=self.pool.get('purchase.order.line').browse(cr,uid,cek)
			cek_available = qty_delivery
			for x in data:
				if x.qty_available_to_pick == cek_available:
					qty = cek_available

					if cek_available > 0:
						line.append({
							'po_id': x.order_id.id,
							'po_line_id':x.id,
							'po_line_product_id':x.product_id.id,
							'po_line_description':x.name,
							'po_line_qty':x.product_qty,
							'po_line_received_items':x.received_items,
							'po_line_available_to_pick':x.qty_available_to_pick,
							'qty':qty,
							'uom_id':x.product_uom.id
						})

					cek_available -= cek_available

				elif x.qty_available_to_pick < cek_available:
					if x.qty_available_to_pick > 0:
						qty = x.qty_available_to_pick

						if cek_available > 0:
							line.append({
								'po_id': x.order_id.id,
								'po_line_id':x.id,
								'po_line_product_id':x.product_id.id,
								'po_line_description':x.name,
								'po_line_qty':x.product_qty,
								'po_line_received_items':x.received_items,
								'po_line_available_to_pick':x.qty_available_to_pick,
								'qty':qty,
								'uom_id':x.product_uom.id
							})

						cek_available -= x.qty_available_to_pick
				elif x.qty_available_to_pick > cek_available:
					qty = cek_available
					
					if cek_available > 0:
						line.append({
							'po_id': x.order_id.id,
							'po_line_id':x.id,
							'po_line_product_id':x.product_id.id,
							'po_line_description':x.name,
							'po_line_qty':x.product_qty,
							'po_line_received_items':x.received_items,
							'po_line_available_to_pick':x.qty_available_to_pick,
							'qty':qty,
							'uom_id':x.product_uom.id
						})
					cek_available -= cek_available
				else:
					qty =0

			res['picked_po'] = line

			return  {'value': res}

	def cek_detail_pb(self, cr, uid, ids, purchase_requisition_id, context=None):
		cek=self.pool.get('detail.pb').search(cr,uid,[('detail_pb_id', '=' ,purchase_requisition_id)])
		hasil=self.pool.get('detail.pb').browse(cr,uid,cek)

		if hasil:
			# Cek Detail PB yang Prosesd Item lebih dari 0 (Sudah di Proses di PO)
			product =[x.name.id for x in hasil if x.jumlah_diminta <> x.delivery_items]
			res = {'domain': {'product_id': [('id','in',tuple(product))]}}
		else:
			res = {
					'warning':{
						'title':'Informasi',
						'message':'Items PB Belum ada yang di terima'
					}
				}
		return res

	def cek_item_pb(self, cr, uid, ids, product_id,purchase_requisition_id, context=None):
		print '=====',product_id
		if product_id :
			res = {}; line = []
			# item_pb=self.pool.get('detail.pb').search(cr,uid,[('id','=',product_id)])
			item_pb=self.pool.get('detail.pb').search(cr,uid,[('name','=',product_id),('detail_pb_id','=',purchase_requisition_id)])
			item=self.pool.get('detail.pb').browse(cr,uid,item_pb)[0]
			cek=self.pool.get('purchase.order.line').search(cr,uid,[('line_pb_general_id', '=' ,item.id)])
			data=self.pool.get('purchase.order.line').browse(cr,uid,cek)
			qty_available = 0
			for x in data:
				if x.qty_available_to_pick > 0:
					line.append({
						'po_id': x.order_id.id,
						'po_line_id':x.id,
						'po_line_product_id':x.product_id.id,
						'po_line_description':x.name,
						'po_line_qty':x.product_qty,
						'po_line_received_items':x.received_items,
						'po_line_available_to_pick':x.qty_available_to_pick,
						'qty':0,
						'uom_id':x.product_uom.id
					})
					qty_available += x.qty_available_to_pick


			res['picked_po'] = line
			res['desc'] = item.name.name
			res['uom_id']=item.satuan.id
			res['qty_delivery']=0
			res['qty_available']=qty_available
			res['purchase_requisition_line_id']=item.id
		return  {'value': res}

	def onchange_product(self, cr, uid, ids, productID, context=None):
		cek=self.pool.get('purchase.order.line').search(cr,uid,[('product_id', '=' ,productID),('state', '=', 'confirmed')])

		hasil=self.pool.get('purchase.order.line').browse(cr,uid,cek)

		for x in hasil:
			if x.received_items > 0:
				product = [x.id]
			else:
				product = []
		return {'domain': {'po_line_id': [('id','in',tuple(product))]}}

	def onchange_po_line(self, cr, uid, ids, poLine, context=None):
		data = self.pool.get('purchase.order.line').browse(cr, uid, poLine)

		cek=self.pool.get('order.requisition.delivery.line').search(cr,uid,[('purchase_requisition_line_id', '=' ,data.line_pb_general_id.id),('state', '=' ,'done')])
		hasil=self.pool.get('order.requisition.delivery.line').browse(cr,uid,cek)
		nilai= 0
		for x in hasil:
			nilai += x.qty_delivery
		return {
				'value':{
						'po_id':data.order_id.id,
						'purchase_requisition_line_id':data.line_pb_general_id.id,
						'desc':data.name,
						'qty_delivery':data.received_items-nilai,
						'qty':data.product_qty,
						'uom_id':data.product_uom.id,
						'received_items_po':data.received_items-nilai,
						}
				}

	def onchange_delivery(self, cr, uid, ids, qty1,qty2, context=None):
		if qty1 > qty2:
			warning = {"title": ("Warning"), "message": ("Product Item Delivery Tidak Mencukupi")}
			return {'warning': warning, 'value': {'qty_delivery': 0}}
		else:
			return False

order_requisition_delivery_line()



class OrderRequisitionDeliveryLinePo(osv.osv):
	_name  = 'order.requisition.delivery.line.po'
	_columns = {
			'order_requisition_delivery_line_id':fields.many2one('order.requisition.delivery.line', 'Order Requisition Delivery Line', required=False,ondelete="CASCADE",onupdate='CASCADE'),
			'po_id':fields.many2one('purchase.order', 'PO No', required=False),
			'po_line_id':fields.many2one('purchase.order.line','Product Item', required=False),
			'po_line_product_id': fields.related('po_line_id','product_id', type='many2one', relation='product.product', string='Product'),
			'po_line_description':fields.related('po_line_id', 'name', type='text', store=False, string='Desc'),
			'po_line_qty':fields.related('po_line_id', 'product_qty', store=False, type='float',string='Qty PO'),
			'po_line_received_items':fields.related('po_line_id','received_items', store=False, type='float',string='Received'),
			'po_line_available_to_pick': fields.related('po_line_id', 'qty_available_to_pick', store=False,type='float', string='Available'),
			'qty':fields.float('Qty',required=False),
			'uom_id':fields.many2one('product.uom', 'UOM', required=False),
	}

	def cek_qty(self, cr, uid, ids, qty1,qty2, context=None):
		if qty2 > qty1:
			warning = {"title": ("Warning"), "message": ("Qty Tidak Mencukupi")}
			return {'warning': warning, 'value': {'qty': 0}}
		else:
			return False

OrderRequisitionDeliveryLinePo()



class stock_move(osv.osv):
	
	_inherit = 'stock.move'
	_columns = {
	        'purchase_line_id': fields.many2one('purchase.order.line','Purchase Order Line', ondelete='set null', select=True,readonly=True),
	        'ref_po_no': fields.related('purchase_line_id', 'no', string='Ref Po No', type='text', store=True),
			'regular_pb_line_id': fields.related('purchase_line_id','line_pb_general_id', type='many2one', relation='detail.pb', string='Regular PB ID'),
			'regular_pb_id': fields.related('regular_pb_line_id','detail_pb_id', type='many2one', relation='pembelian.barang', string='Regular PB No'),
			'regular_pb_no': fields.related('regular_pb_id','name', type='char', string='Regular PB No'),
			'regular_pb_request_by': fields.related('regular_pb_id','employee_id', type='many2one', relation='hr.employee', string='Request By'),
			'regular_pb_department_requested': fields.related('regular_pb_id','department_id', type='many2one', relation='hr.department', string='Department Request By'),
			'regular_pb_destination_request': fields.related('regular_pb_id','destination_location_request_id', type='many2one', relation='stock.location', string='Destination Request'),
			'regular_pb_due_date': fields.related('regular_pb_id','duedate', type='date', string='Due Date'),

	}



stock_move()

class stock_partial_picking_line(osv.osv):

	_inherit = "stock.partial.picking.line"
	_columns = {
		'move_id' : fields.many2one('stock.move', "Move", ondelete='CASCADE'),
		'ref_po_no': fields.related('move_id', 'ref_po_no', string='Ref No', type='text', store=False),
	}


stock_partial_picking_line()


class stock_partial_picking(osv.osv_memory):
	
	_inherit = "stock.partial.picking"

	def _partial_move_for(self, cr, uid, move, context={}):
		partial_move = {
			'ref_po_no':move.ref_po_no,
			'product_id' : move.product_id.id,
			'product_name':move.name,
			'quantity' : move.product_qty if move.state == 'assigned' or move.picking_id.type == 'in' else 0,
			'product_uom' : move.product_uom.id,
			'prodlot_id' : move.prodlot_id.id,
			'move_id' : move.id,
			'location_id' : move.location_id.id,
			'location_dest_id' : move.location_dest_id.id,
		}
		if move.picking_id.type == 'in' and move.product_id.cost_method == 'average':
			partial_move.update(update_cost=True, **self._product_cost_for_average_update(cr, uid, move))
		return partial_move