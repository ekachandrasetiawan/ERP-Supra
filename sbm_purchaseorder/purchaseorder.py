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
	}
	
	def create(self, cr, uid, vals, context=None):
		if 'name' in vals:
			vals['name'] = vals['name']
		else:
			vals['name'] = int(time.time())

		print '=============time=-====',int(time.time())

		print '===========',vals['name']
		
		return super(Purchase_Order_Sbm, self).create(cr, uid, vals, context=context)

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
		val = self.browse(cr, uid, ids)[0]
		obj_pb = self.pool.get('pembelian.barang')
		obj_detail_pb = self.pool.get('detail.pb')

		for po in self.browse(cr, uid, ids, context=context):
			if po.type_permintaan == '1':
				cek = self.pool.get('purchase.order.line').search(cr,uid,[('order_id', '=' ,ids)])
				obj_purchase_line = self.pool.get('purchase.order.line').browse(cr,uid, cek)
				
				result = []
				for z in obj_purchase_line:
					row = []
					if z.line_pb_general_id:
						pb_id = z.line_pb_general_id.detail_pb_id.id

						detail_pb_cek=self.pool.get('detail.pb').search(cr,uid,[('id', '=' ,z.line_pb_general_id.id)])
						valdetailpb = self.pool.get('detail.pb').browse(cr,uid,detail_pb_cek[0])

						# Append Data PB ID dan Detail PB ID
						row.append(valdetailpb.id)
						row.append(valdetailpb.detail_pb_id.id)

						#  Cek Qty Available Detail PB, Jika hasil nya 0 maka update state Detail PB
						if valdetailpb.qty_available == 0.0:
							self.pool.get('detail.pb').write(cr, uid, [z.line_pb_general_id.id], {'state':'proses'})

					result.append(row)

				# Prosess Send Email
				if row:
					self.proses_send_email(cr, uid, ids, result, context=None)

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


	def copy_pure_purchase_order(self,cr,uid,ids,fiscal_position_id=False,context=None):
		val = self.browse(cr,uid,ids,context)[0]
		po_obj = self.pool.get('purchase.order')
		account_fiscal_position = self.pool.get('account.fiscal.position')
		account_tax = self.pool.get('account.tax')
		lines = []
		for line in val.order_line:
			taxes = account_tax.browse(cr, uid, map(lambda line: line.id, line.product_id.supplier_taxes_id))
			fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
			taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
			
			if line.product_id.active == True:
				lines.append((0,0,{
						'no'			:line.no,
						'product_id'	:line.product_id.id,
						'variants'		:line.variants.id,
						'name'			:line.name,
						'part_number'	:line.part_number,
						'date_planned'	:line.date_planned,
						'product_qty'	:line.product_qty,
						'product_uom'	:line.product_uom.id,
						'price_unit'	:0,
						'note_line'		:'-',
						'taxes_id'		:[(6,0,taxes_ids)],
					}))
			else:
				raise osv.except_osv(_('Error'),_('Product '+line.product_id.default_code+ " is not active in system.\r\nPlease activate it first."))

		po_id = po_obj.create(cr, uid, {
				'name':int(time.time()),
				'date_order': time.strftime("%Y-%m-%d"),
				'duedate':time.strftime("%Y-%m-%d"),
				'partner_id': val.partner_id.id,
				'jenis': val.jenis,
				'pricelist_id': val.pricelist_id.id,
				'location_id': val.location_id.id,
				'origin':val.origin,
				'type_permintaan':val.type_permintaan,
				'term_of_payment':val.term_of_payment,
				'order_line':lines
			})


		pool_data=self.pool.get("ir.model.data")
		action_model,action_id = pool_data.get_object_reference(cr, uid, 'purchase', "purchase_order_form")     
		action_pool = self.pool.get(action_model)
		res_id = action_model and action_id or False
		action = action_pool.read(cr, uid, action_id, context=context)
		action['name'] = 'purchase.order.form'
		action['view_type'] = 'form'
		action['view_mode'] = 'form'
		action['view_id'] = [res_id]
		action['res_model'] = 'purchase.order'
		action['type'] = 'ir.actions.act_window'
		action['target'] = 'current'
		action['res_id'] = po_id

		return action


	def proses_send_email(self, cr, uid, ids, result, context=None):
		# Pengelompokan PB Line ID sesuai Dengan PB ID nya
		order=[]
		dic=dict()
		for value,key in result:
		  try:
			dic[key].append(value)
		  except KeyError:
			order.append(key)
			dic[key]=[value]
		newlist=map(dic.get, order)

		# Pengelompokan PB Line ID dengan Employee ID
		data = []
		for nilai in newlist:
			column = []
			for x in nilai:
				row = []
				pb_line = self.pool.get('detail.pb').browse(cr, uid, x, context=None)
				row.append(pb_line.id)
				row.append(pb_line.detail_pb_id.employee_id.id)
				column.append(row)

			data.append(column)

		dt_line = []
		for data_array in data:
			for x in data_array:
				dt_line.append(x)

		order_1=[]
		dic_1=dict()
		for value,key in dt_line:
		  try:
			dic_1[key].append(value)
		  except KeyError:
			order_1.append(key)
			dic_1[key]=[value]
		newlist_1=map(dic_1.get, order_1)

		for lines in newlist_1:
			employee_id = False
			email_to = False
			partner_id = False
			for x in lines:
				pb_line_id = self.pool.get('detail.pb').browse(cr, uid, x, context=None)

				employee_id = pb_line_id.detail_pb_id.employee_id.id
				employee_name = pb_line_id.detail_pb_id.employee_id.name
				email_to = pb_line_id.detail_pb_id.employee_id.user_id.email
				partner_id = pb_line_id.detail_pb_id.employee_id.user_id.partner_id.id

			self.data_email(cr, uid, ids, lines, employee_id, employee_name, email_to, partner_id, context=None)

		return True


	def data_email(self, cr, uid, ids, lines, employee_id, employee_name, email_to, partner_id, context=None):
		val = self.browse(cr, uid, ids)[0]
		obj_pb = self.pool.get('pembelian.barang')

		body = self.template_email(cr, uid, ids, lines, employee_name, context=None)
		subject = 'Telah di release PO #' + val.name

		send_email = self.send_email(cr, uid, ids, val.id, subject, email_to, partner_id, body, context={})
		return True

	def template_email(self, cr, uid, ids, lines, employee_name, context=None):
		val = self.browse(cr, uid, ids)[0]

		ip_address = '192.168.9.26:10001'
		db = 'LIVE_2014'
		url = 'http://'+ip_address+'/?db='+db+'#id=' +str(val.id)+'&view_type=form&model=purchase.order&menu_id=330&action=394'

		data_table = '<table border="1"><tr><th>Purchase Requisition No</th><th>Product</th><th>Qty (PO)</th></tr>'
		for x in lines:
			qty = 0
			uom = False
			for c in val.order_line:
				if c.line_pb_general_id.id == x:
					qty = c.product_qty
					uom = c.product_uom.name

			pb_line = self.pool.get('detail.pb').browse(cr, uid, x, context=None)
			data_table += '<tr><td>'+ str(pb_line.detail_pb_id.name) +'</td><td>' + '['+ pb_line.name.default_code +']' + pb_line.name.name +'</td><td>'+ str(qty) + ' ' + str(uom) + '</td></tr>'
		
		data_table += '</table>'

		body = """\
			<html>
			  <head></head>
			  <body>
				<p>
					Dear %s!<br/><br/>
					Telah di release PO # %s untuk memenuhi permintaan
					<br/>
					<b>Detail Barang :</b><br/>
					%s
					<br/>
					Silahkan klik Link ini untuk melihat Purchase Oder. <a href="%s">View Purchase Order</a>
				</p>
				<br/>
				Best Regards,<br/>
				Administrator ERP
			  </body>
			</html>
			""" % (employee_name, val.name, data_table, url)

		return body


	def send_email(self, cr, uid, ids, po_id, subject, email_to, partner_id, body, context=None):
		val = self.browse(cr, uid, ids)[0]
		mail_mail = self.pool.get('mail.mail')
		obj_usr = self.pool.get('res.users')
		obj_partner = self.pool.get('res.partner')

		username = obj_usr.browse(cr, uid, uid)

		mail_id = mail_mail.create(cr, uid, {
			'model': 'purchase.order',
			'res_id': po_id,
			'subject': subject,
			'body_html': body,
			'auto_delete': True,
			}, context=context)

		mail_mail.send(cr, uid, [mail_id], recipient_ids=[partner_id], context=context)

		return True

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
	
	def _get_stock_move(self,cr,uid,ids,context={}):
		res = {}
		for line in self.pool.get('stock.move').browse(cr,uid,ids,context=context):
			res[line.purchase_line_id.id]=True
		return res.keys()

	_inherit = 'purchase.order.line'
	_columns = {
		'no':fields.integer('No'),
		'line_pb_general_id':fields.many2one('detail.pb', 'Detail PB Umum'),
		'note_line':fields.text('Notes line'),
		'part_number':fields.char('Part Number'),
		'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True),
		'variants':fields.many2one('product.variants','variants'),
		'date_planned':fields.date('Scheduled Date', select=True),
		'received_items': fields.function(_get_received,string="Received Items",type="float",readonly=False,
			store={
				'purchase.order.line': (lambda self, cr, uid, ids, c={}: ids, ['product_id','product_qty','state','supplied_items','qty_available_to_pick'], 20),
				'stock.move': (_get_stock_move, ['product_qty','state'], 20),
			}),
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