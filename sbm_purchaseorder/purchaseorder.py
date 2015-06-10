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
						self.pool.get('detail.pb').write(cr, uid, [z.line_pb_general_id.id], {'qty_available': valdetailpb.jumlah_diminta-z.product_qty})

						if valdetailpb.jumlah_diminta-z.product_qty == 0:
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
		
		self.write(cr, uid, ids, {'state': 'approved', 'date_approve': fields.date.context_today(self,cr,uid,context=context)})
		return super(Purchase_Order_Sbm,self).wkf_approve_order(cr,uid,ids,context=context)
	
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
					
				#self.write(cr,uid,ids,{'state':'approved'})
				self.write(cr,uid,ids,{'state':'cancel'})
				
			for (id, name) in self.name_get(cr, uid, ids):
				wf_service.trg_validate(uid, 'purchase.order', id, 'purchase_cancel', cr)
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

class purchase_order_line_detail(osv.osv):
	_inherit = 'purchase.order.line'
	_columns = {
		'no':fields.integer('No'),
		'line_pb_general_id':fields.many2one('detail.pb', 'Detail PB Umum'),
		'note_line':fields.text('Notes line'),
		'part_number':fields.char('Part Number'),
		'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True),
		'variants':fields.many2one('product.variants','variants'),
		'date_planned':fields.date('Scheduled Date', select=True),
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
		res['domain'] =False
		res['domain'] = {'variants': [('product_id','=',product_id)]}
		# print '===============================================ok=================',res
		return res

	def onchange_product_new(self, cr, uid, ids, product, product_uom, context=None):
		if product:
			product_id =self.pool.get('product.product').browse(cr,uid,product)
			if product_id.categ_id.id == 12:
				uom=product_uom
			else:
				if product_id.sale_ok and product_id.purchase_ok:
					uom=product_uom
				else:
					uom=product_id.uom_id.id
		else:
			uom=product_uom
		return {'value':{'product_uom':uom}}

		
purchase_order_line_detail()
