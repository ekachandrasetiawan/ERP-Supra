import datetime
import time
import netsvc
from openerp.tools.translate import _
from osv import osv, fields

class Purchase_Order_Sbm(osv.osv):
	_inherit = 'purchase.order'
	# CONTOH FIELD FUNCTION
	def _getStateAlert(self, cr, uid, ids, fields, arg, context):
		x={}
		date_format = "%Y-%m-%d"
		now = datetime.datetime.now()
		valDate = now.strftime('%Y-%m-%d')
		# print "**************************************************",type(now)
		# todayIs = datetime.datetime.strptime(, "%Y-%m-%d")

		

		for record in self.browse(cr, uid, ids):
			if record.duedate :
				a = datetime.datetime.strptime(record.duedate, "%Y-%m-%d")
				# print "**************************************************",type(a)
				b = now-a
				x[record.id] = b.days
			else:
				x[record.id] = "-"
		return x
	_columns = {
		'name': fields.char('Order Reference', size=64, required=True, select=True, help="Unique number of the purchase order, computed automatically when the purchase order is created."),
		'duedate':fields.date('Due Date',required=True),
		'partner_id':fields.many2one('res.partner', 'Supplier', required=True, states={'confirmed':[('readonly',True)], 'approved':[('readonly',False)],'done':[('readonly',True)]},
			change_default=True, track_visibility='always'),
		'attention': fields.many2one('res.partner', 'Attention', domain="[('parent_id', '=', partner_id)]"),
		'no_fpb':fields.char('Nomor F-PB'),
		'type_permintaan':fields.selection([('1','umum'),('2','rental'),('3','Sub Count')],'Type Permintaan',required=True,states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]},),
		'detail_po_ids': fields.many2many('detail.pb','wizard_pb_rel','detail_pb_id','wizard_id','List Permintaan Barang'),
		'print_line':fields.integer('Line Print'),
		'shipment_to_product':fields.many2one('stock.location','Stock Location'),
		'submit_no':fields.char('Submit No'),
		'jenis': fields.selection([('loc', 'Local Regular'),('loc-petty', 'Local Regular Petty'), ('impj', 'Import J'), ('imps', 'Import S')], 'Type', readonly=True,required=True, states={'draft':[('readonly',False)]}, select=True),
		'stateAlert': fields.function(
			_getStateAlert,
			string="Due Date Month",type="char"
		),
	}
	
	_defaults ={
		'location_id':12,
		'print_line':10,
		'name':int(time.time()),
		# 'duedate' : time.strftime('%Y-%m-%d')
	}
	
	def create(self, cr, uid, vals, context=None):
		order =  super(Purchase_Order_Sbm, self).create(cr, uid, vals, context=context)
		return order

	def print_po_out(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"purchase-order/printpo&id="+str(ids[0])+"&uid="+str(uid)

		return {
			'type'  : 'ir.actions.client',
			'target': 'new',
			'tag'   : 'print.out.po',
			'params': {
				# 'id'  : ids[0],
				'redir' : urlTo,
				'uid':uid
			},
		}

	def on_change_partner_id(self,cr,uid,ids, pid):
		partner_id = self.pool.get('res.partner').browse(cr,uid, pid)
		cek=self.pool.get('res.partner').search(cr,uid,[('parent_id', '=' ,partner_id.id)])

		hasil=self.pool.get('res.partner').browse(cr,uid,cek)
		parent =[x.id for x in hasil]
		return {'domain': {'attention': [('id','in',tuple(parent))]}}


	def wkf_approve_order(self, cr, uid, ids, context=None):
		for po in self.browse(cr, uid, ids, context=context):
			if po.jenis == 'impj':
				no = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.importj')
			elif po.jenis == 'imps':
				no = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.imports')
			else:
				no = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order')

			print no;

			if po.type_permintaan == '1':

				# cek = self.pool.get('detail.order.line').search(cr,uid,[('order_line_id', '=' ,ids)])
				# order_line =self.pool.get('detail.order.line').browse(cr,uid,cek)
				# for x in order_line:
				# 	detail_pb_cek=self.pool.get('detail.pb').search(cr,uid,[('id', '=' ,x.detail_pb_id)])
				# 	valdetailpb = self.pool.get('detail.pb').browse(cr,uid, detail_pb_cek[0])
				# 	self.pool.get('detail.pb').write(cr, uid, [x.detail_pb_id], {'qty_available': valdetailpb.jumlah_diminta-x.qty})
				# 	if valdetailpb.jumlah_diminta-x.qty == 0:
				# 		self.pool.get('detail.pb').write(cr, uid, [x.detail_pb_id], {'state':'proses'})
				#print '--------------------------------',ids
				# obj_purchase_line = self.pool.get('purchase.order.line').browse(cr,uid,[('order_id', '=' ,)])
				cek = self.pool.get('purchase.order.line').search(cr,uid,[('order_id', '=' ,ids)])

				obj_purchase_line = self.pool.get('purchase.order.line').browse(cr,uid, cek)
				
				for z in obj_purchase_line:
					if z.line_pb_general_id:
						detail_pb_cek=self.pool.get('detail.pb').search(cr,uid,[('id', '=' ,z.line_pb_general_id.id)])
						
						valdetailpb = self.pool.get('detail.pb').browse(cr,uid,detail_pb_cek[0])
						#  Cek Qty Available Detail PB, Jika hasil nya 0 maka update state Detail PB
						if valdetailpb.qty_available == 0:
							self.pool.get('detail.pb').write(cr, uid, [z.line_pb_general_id.id], {'state':'proses'})
			elif po.type_permintaan == '2':
				# loop each order line
				for line in po.order_line:
					# if line_pb_rent_id is not null then update rent requisition detail state
					if line.line_pb_rent_id:
						self.pool.get('rent.requisition.detail').write(cr,uid,[line.line_pb_rent_id.id],{'state':'process'})
			elif po.type_permintaan == '3':
				for line in po.order_line:
					if line.line_pb_subcont_id:
						self.pool.get('purchase.requisition.subcont.line').write(cr,uid,[line.line_pb_subcont_id.id],{'state_line':'po'})

		return super(Purchase_Order_Sbm,self).wkf_approve_order(cr,uid,ids,context=context)
	
	def _create_pickings(self, cr, uid, order, order_lines, picking_id=False, context=None):

		res = super(Purchase_Order_Sbm,self)._create_pickings(cr,uid,order, order_lines, picking_id=False,context=context)

		return res

	def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
		
		if order_line.part_number == False:
			nameproduct = order_line.name or ''
		else:
			nameproduct = order_line.name + ' '  +  '[' + order_line.part_number + ']' or ''

		return {
			'name': nameproduct,
			'product_id': order_line.product_id.id,
			'product_qty': order_line.product_qty,
			'product_uos_qty': order_line.product_qty,
			'product_uom': order_line.product_uom.id,
			'product_uos': order_line.product_uom.id,
			'date': self.date_to_datetime(cr, uid, order.date_order, context),
			'date_expected': self.date_to_datetime(cr, uid, order_line.date_planned, context),
			'location_id': order.partner_id.property_stock_supplier.id,
			'location_dest_id': order.location_id.id,
			'picking_id': picking_id,
			'partner_id': order.dest_address_id.id or order.partner_id.id,
			'move_dest_id': order_line.move_dest_id.id,
			'state': 'draft',
			'type':'in',
			'purchase_line_id': order_line.id,
			'company_id': order.company_id.id,
			'price_unit': order_line.price_unit
		}
		
	def action_cancel(self, cr, uid, ids, context=None):

		wf_service = netsvc.LocalService("workflow")
		for purchase in self.browse(cr, uid, ids, context=context):
			cek=self.pool.get('detail.order.line').search(cr,uid,[('order_line_id', '=' ,ids)])
			order_line =self.pool.get('detail.order.line').browse(cr,uid,cek)
			for val in order_line:
				# ================== Update Detail PB menjadi Confirm ===================
				self.pool.get('detail.pb').write(cr, uid, [val.detail_pb_id], {'state':'onproses'})
				# ================== Cek Qty Detail PB =================================
				Qty_PB=self.pool.get('detail.pb').search(cr,uid,[('id', '=' ,val.detail_pb_id)])
				QtyDetail = self.pool.get('detail.pb').browse(cr,uid, Qty_PB[0])
				self.pool.get('detail.pb').write(cr, uid, [val.detail_pb_id], {'qty_available':QtyDetail.qty_available+val.qty})

			for pick in purchase.picking_ids:
				if pick.state not in ('draft','cancel'):
					raise osv.except_osv(
						_('Unable to cancel this purchase order.'),
						_('First cancel all receptions related to this purchase order.'))
			for pick in purchase.picking_ids:
				wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_cancel', cr)
			for inv in purchase.invoice_ids:
				if inv and inv.state not in ('cancel','draft'):
					raise osv.except_osv(
						_('Unable to cancel this purchase order.'),
						_('You must first cancel all receptions related to this purchase order.'))
				if inv:
					wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)
				self.write(cr,uid,ids,{'state':'cancel'})
				
			for (id, name) in self.name_get(cr, uid, ids):
				wf_service.trg_validate(uid, 'purchase.order', id, 'purchase_cancel', cr)


		# Cancel Purchase Order Line
		po_line=self.pool.get('purchase.order.line').search(cr,uid,[('order_id', '=' ,ids)])
		order_line =self.pool.get('purchase.order.line').browse(cr,uid,po_line)
		for x in order_line:
			self.pool.get('purchase.order.line').write(cr, uid, [x.id], {'state':'cancel'})


		return True
	
	def setdraft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'draft'})

	def reportpo(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		datas = {'ids': context.get('active_ids', [])}
		datas['model'] = 'purchase.order'
		datas['form'] = self.read(cr, uid, ids)[0]
		
		return {
			'type': 'ir.actions.report.xml',
			'report_name': 'report.purchase.order',
			'report_type': 'webkit',
			'datas': datas,
		}

Purchase_Order_Sbm()


class purchase_order_patty(osv.osv):
    _name = "purchase.order.petty"
    _inherit = "purchase.order"
    _table = "purchase_order"
    _description = "Purchase Order Petty"

    _columns = {
    		'jenis':fields.selection([('loc','Local Regular'),('loc-petty','Local Regular Petty'),('impj','Import J'),('imps','Import S')],'Jenis'),
    }


purchase_order_patty()




class purchase_order_line_detail(osv.osv):
	
	def _get_received(self,cr,uid,ids,field_name,args,context={}):		
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			move=self.pool.get('stock.move').search(cr,uid,[('purchase_line_id', '=' ,item.id), ('state', '=', 'done')])
			hasil= 0
			for data in  self.pool.get('stock.move').browse(cr,uid,move):
				hasil += data.product_qty
			res[item.id] = hasil
		return res

	def _get_supplied_items(self,cr,uid,ids,field_name,args,context={}):		
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			move=self.pool.get('order.requisition.delivery.line.po').search(cr,uid,[('po_line_id', '=' ,item.id)])
			hasil= 0
			for data in  self.pool.get('order.requisition.delivery.line.po').browse(cr,uid,move):
				hasil += data.qty
			res[item.id] = hasil
		return res

	def _get_qty_available_to_pick(self,cr,uid,ids,field_name,args,context={}):		
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			move=self.pool.get('purchase.order.line').search(cr,uid,[('id', '=' ,item.id)])
			hasil= 0
			for data in  self.pool.get('purchase.order.line').browse(cr,uid,move):
				hasil += data.received_items-data.supplied_items
			res[item.id] = hasil
		return res
		

	_inherit = 'purchase.order.line'
	_columns = {
		'no':fields.integer('No'),
		'line_pb_general_id':fields.many2one('detail.pb', 'Detail PB Umum'),
		'note_line':fields.text('Notes line'),
		'part_number':fields.char('Part Number'),
		'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True),
		'variants':fields.many2one('product.variants','variants'),
		'date_planned':fields.date('Scheduled Date', select=True),
		'received_items': fields.function(_get_received,string="Received Items",type="float",store=False, readonly=False),
		'supplied_items': fields.function(_get_supplied_items,string="Supplied Items",type="float",store=False, readonly=False),
		'qty_available_to_pick': fields.function(_get_qty_available_to_pick,string="Available To Pick",type="float",store=False, readonly=False),
		}

	_defaults ={
		'no':1,
	}
	_order = 'no ASC'

	def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
			partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
			name=False, price_unit=False, context=None):
		res = super(purchase_order_line_detail,self).onchange_product_id(cr,uid,ids,pricelist_id, product_id, qty, uom_id,
			partner_id, date_order, fiscal_position_id, date_planned,
			name, price_unit, context)

		if product_id:
			cek=self.pool.get('product.variants').search(cr,uid,[('product_id', '=' ,product_id)])
			hasil=self.pool.get('product.variants').browse(cr,uid,cek)
			products=self.pool.get('product.product').browse(cr,uid,product_id)
			pn = products.default_code
			product =[x.id for x in hasil]
			variants=[('id','in',tuple(product))]
			res['value']['product_uom'] = products.uom_id.id
		res['domain'] =False
		res['domain'] = {'variants': [('product_id','=',product_id)]}
		return res

	def onchange_product_new(self, cr, uid, ids, product, product_uom, context=None):
		if product:
			product_id =self.pool.get('product.product').browse(cr,uid,product)
			if product_id.categ_id.id == 12:
				uom=product_uom
			else:
				if product_id.sale_ok == False and product_id.purchase_ok:
					uom=product_uom
					print "aaaa========================"
				else:
					uom=product_id.uom_id.id
					print "bbbb=========================="
		else:
			uom=product_uom
			print "ccc"
		return {'value':{'product_uom':uom}}

		
purchase_order_line_detail() 