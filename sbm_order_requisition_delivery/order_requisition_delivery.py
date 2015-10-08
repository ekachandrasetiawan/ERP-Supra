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
			line = [data.purchase_requisition_line_id.detail_pb_id.name[:5] for data in self.pool.get('order.requisition.delivery.line').browse(cr,uid,move)]
			hasil= ''
			for x in set(line):
				hasil += x + ', '
			res[item.id] = hasil
		return res


	_name = 'order.requisition.delivery'
	_columns = {
		'name':fields.char('Refference',required=True, readonly=False),
		'source_location': fields.many2one('stock.location', "Source Location", required=True),
		'destination_location_id': fields.many2one('stock.location', "Destination Location", required=True),
		'date':fields.datetime('Date',required=True),
		'pr_names': fields.function(_get_pr_names,string="PR Names",type="char",store=False, readonly=False),
		'notes':fields.text('Date',required=False),
		'lines': fields.one2many('order.requisition.delivery.line', 'order_requisition_delivery_id', 'Lines',readonly=False),
		'state': fields.selection([
			('draft', 'Draft'),
			('confirmed', 'Confirmed'),
			('approved', 'Approved'),
			('done','Done'),
			],
			'State'),
		'picking_id': fields.many2one('stock.picking', "Stock Picking", required=False, readonly=True),
		'approved_by':fields.many2one('res.users',string="Approved By",ondelete="CASCADE",onupdate='CASCADE'),
		'received_by':fields.many2one('res.users',string="Received By",ondelete="CASCADE",onupdate='CASCADE'),
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


	def create(self, cr, uid, vals, context=None):
		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'order.requisition.delivery')
		return super(order_requisition_delivery, self).create(cr, uid, vals, context=context)

	def def_confirmed(self,cr,uid,ids,context=None):

		return self.write(cr,uid,ids,{'state':'confirmed'})

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
					'product_id': line.name.id,
					'product_qty': line.qty_delivery,
					'product_uom': line.uom_id.id,
					'location_id' : val.source_location.id,
					'location_dest_id' : val.destination_location_id.id,
					'picking_id': picking,
					'state':'done'
					},context=context)

				self.pool.get('order.requisition.delivery').write(cr, uid, line.id, {'state':'done'}, context=context)

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
				hasil += data.received_items
			res[item.id] = hasil
		return res


	_name = 'order.requisition.delivery.line'
	_columns = {
		'name': fields.many2one('product.product', "Product", required=True, select=True),
		'order_requisition_delivery_id':fields.many2one('order.requisition.delivery', 'Order Requisition Delivery', required=True, ondelete='cascade',change_default=True),
		'po_line_id':fields.many2one('purchase.order.line', 'Purchase Order Line', required=True, ondelete='cascade',change_default=True,select=True),
		'purchase_requisition_id':fields.many2one('pembelian.barang', 'Purchase Requisition', required=False, ondelete='cascade',select=True),
		'purchase_requisition_line_id':fields.many2one('detail.pb', 'Purchase Requisition Line', required=False, ondelete='cascade',select=True),
		'po_id':fields.many2one('purchase.order',string='No Purcahse Order'),
		'desc':fields.text('Description', required=False),
		'move_id':fields.many2one('stock.move', 'Stock Move', required=False, ondelete='cascade'),
		'qty_delivery':fields.float('Qty Items Delivery', required=False,readonly=False),
		'qty':fields.float('Qty Items PO', required=False,readonly=False),
		'received_items_po': fields.float(string="Received Items", readonly=False),	
		'uom_id':fields.many2one('product.uom', 'UOM', required=False),
		'qty_available': fields.function(_get_qty_available,string="Qty Available",type="float",store=False),
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
			'order_requisition_delivery_line_id':fields.many2one('order.requisition.delivery.line', 'Order Requisition Delivery Line', required=True),
			'po_id':fields.many2one('purchase.order', 'Purchase Order', required=True),
			'po_line_id':fields.many2one('purchase.order.line','Purchase Order Line', required=True),
			'po_line_product_id':fields.related('po_line_id', 'product_id', type='many2one', store=False),
			'po_line_description':fields.related('po_line_id', 'name', type='text', store=False),
			'po_line_qty':fields.related('po_line_id', 'product_qty', store=False, type='float'),
			'po_line_received_items':fields.related('po_line_id','received_items', store=False, type='float'),
			'po_line_available_to_pick': fields.related('po_line_id', 'avaialble_to_pick', store=False,type='float')
	}


class pembelian_barang(osv.osv):
	_inherit = 'pembelian.barang'
	_columns = {
		'source_location_request_id': fields.many2one('stock.location', "Source Location", readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]}),
		'destination_location_request_id': fields.many2one('stock.location', "Destination Location", required=True, readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]}),
		
	}

	_defaults = {
		'source_location_request_id': 12,
	}

pembelian_barang()


class detail_pb(osv.osv):

	def _get_delivery_items(self,cr,uid,ids,field_name,args,context={}):		
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			# move=self.pool.get('purchase.order.line').search(cr,uid,[('line_pb_general_id', '=' ,item.id)])
			hasil= 0
			# for data in  self.pool.get('purchase.order.line').browse(cr,uid,move):
			# 	hasil += data.received_items
			res[item.id] = hasil
		return res

	def _get_processed_items(self,cr,uid,ids,field_name,args,context={}):		
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			move=self.pool.get('purchase.order.line').search(cr,uid,[('line_pb_general_id', '=' ,item.id)])
			hasil= 0
			for data in  self.pool.get('purchase.order.line').browse(cr,uid,move):
				hasil += data.received_items
			res[item.id] = hasil
		return res

	_name = 'detail.pb'
	_inherit = 'detail.pb'
	_columns = {
		'delivery_items': fields.function(_get_delivery_items,string="Received Items",type="float",store=False),
		'processed_items': fields.function(_get_processed_items,string="Processed Items",type="float",store=False),
	}


detail_pb()
