import time
from datetime import date, timedelta, datetime
import netsvc
from tools.translate import _
from osv import osv, fields

class Pembelian_Barang(osv.osv):
	
	STATES = [
		('draft', 'Draft'),
		('confirm', 'Check'),
		('confirm2', 'Confirm'),
		('purchase','Purchase'),
		('done', 'Done'),
		('cancel', 'Cancel'),
		('edit','Edit PB')
	]

	# FOR STATE FIELD
	def _getParentState(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		for data in self.browse(cr,uid,ids,context):

			line = [x.id for x in data.detail_pb_ids]
			state_done =[y.id for y in data.detail_pb_ids if y.state =="done"]
			
			operation = context.get('operation',False)
			action_state = context.get('action_state',False)

			# print '====aaaa=========',operation
			# print '====bbbb=========',action_state

			if line  == state_done :
				res[data.id] = "done"

			if operation == "create":
				res[data.id] = "draft"
			elif action_state == "submit":
				res[data.id] = "confirm"
			elif action_state == "confirm":
				res[data.id] = "confirm2"
			elif action_state == "confirm2":
				res[data.id] = "purchase"
			elif action_state == "draft":
				res[data.id] = "draft"
			
			# elif data.state=="draft":
			# 	res[data.id] = "draft"
			# elif data.state=="confirm":
			# 	res[data.id] = "confirm"
			# elif data.state=="confirm2":
			# 	res[data.id] = "confirm2"
			# elif data.state=="purchase":
			# 	res[data.id] = "purchase"

		return res


	def _get_cek_state_detail_pb(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('detail.pb').browse(cr, uid, ids, context=context):
			result[line.detail_pb_id.id] = True
		return result.keys()


	def _get_cek_state_delivery_line(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('order.requisition.delivery.line').browse(cr, uid, ids, context=context):
			result[line.purchase_requisition_line_id.detail_pb_id.id] = True
		return result.keys()


	_name = 'pembelian.barang'
	_columns = {
		'name':fields.char('No.PB',required=True, readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]}),
		'spk_no':fields.char('SPK No / PO No',readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]},track_visibility='onchange'),
		'tanggal':fields.date('Date', required=True,readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]}),
		'duedate':fields.date('Due Date',required=True,readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]}),
		'employee_id': fields.many2one('hr.employee', "Employee",required=True, readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]}),
		'department_id':fields.many2one('hr.department','Department',readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]}),
		'customer_id':fields.many2one('res.partner','Customer', domain=[('customer','=',True)],readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]}),
		'detail_pb_ids': fields.one2many('detail.pb', 'detail_pb_id', 'Detail PB',readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]},track_visibility='onchange'),
		'ref_pb':fields.char('Ref No',required=True, select=True,readonly=True,states={'draft':[('readonly',False)],'edit':[('readonly',False)]},track_visibility='onchange'),
		'notes': fields.text('Terms and Conditions',readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]}),
		'cancel_reason':fields.text('Cancel Reason'),
		'product_id': fields.related('detail_pb_ids','name', type='many2one', relation='product.product', string='Product'),
		'source_location_request_id': fields.many2one('stock.location', "Source Location", readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]}),
		'destination_location_request_id': fields.many2one('stock.location', "Destination Location", required=True, readonly=True, states={'draft':[('readonly',False)],'edit':[('readonly',False)]}),
		# 'state': fields.selection(STATES,string="State"),
		'state':fields.function(_getParentState,method=True,string="State",type="selection",selection=STATES,
			store={
				'pembelian.barang': (lambda self, cr, uid, ids, c={}: ids, ['state'], 20),
				'detail.pb': (_get_cek_state_detail_pb, ['state'], 20),
				'order.requisition.delivery.line': (_get_cek_state_delivery_line, ['state'], 20),
			}),
	}
	_inherit = ['mail.thread']

	_track = {
		'state':{
			'sbm_purchase.pb_confirmed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm',
			'sbm_purchase.pb_checked': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm2',
			'sbm_purchase.pb_canceled': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
			'sbm_purchase.pb_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
		},
	}


	def _employee_get(obj, cr, uid, context=None):
		if context is None:
			context = {}

		cek=obj.pool.get('hr.employee').search(cr,uid,[('user_id', '=' ,uid)])
		hasil=obj.pool.get('hr.employee').browse(cr,uid,cek)

		if hasil:
			ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
			if ids:
				return ids[0]
		else:
			return uid
			

	_defaults = {
		'name': '/',
		'tanggal':time.strftime('%Y-%m-%d'),
		'employee_id': _employee_get,
		'state': 'draft',
		'source_location_request_id': 12,
	}

	_order = 'id DESC'



	def action_cancel_item(self,cr,uid,ids,context=None):
		if context is None:
			context = {}
		
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_purchase', 'wizard_pr_cancel_form')

		context.update({
			'active_model': self._name,
			'active_ids': ids,
			'active_id': len(ids) and ids[0] or False
		})
		return {
			'view_mode': 'form',
			'view_id': view_id,
			'view_type': 'form',
			'view_name':'wizard_pr_cancel_form',
			'res_model': 'pembelian.barang',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
			'nodestroy': True,
		}


	def setDeuDate(self, cr, uid, ids, tanggal):
		setDueDateValue = datetime.strptime(tanggal, "%Y-%m-%d") + timedelta(days=4)
		return {'value':{'duedate':setDueDateValue.strftime('%Y-%m-%d')}}

	def setTanggal(self, cr, uid, ids, tanggal, duedate):
		setDueDateValue = datetime.strptime(tanggal, "%Y-%m-%d") + timedelta(days=4)
		cektanggal = setDueDateValue.strftime("%Y-%m-%d")
		if duedate < cektanggal:
			return {'value':{'duedate':cektanggal}}
		else:
			return {'value':{'duedate':duedate}}
		
	def create(self, cr, uid, vals, context={}):
		# vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'pembelian.barang')
		context.update(action_state='confirm')
		return super(Pembelian_Barang, self).create(cr, uid, vals, context=context)


	def setDept(self,cr,uid,ids,pid):
		employee_id = self.pool.get('hr.employee').browse(cr,uid,pid)
		dept_id = employee_id.department_id.id
		return {'value':{ 'department_id':dept_id} }

	
	def submit(self,cr,uid,ids,context={}):
		context.update(action_state='submit')
		val = self.browse(cr, uid, ids)[0]
		code = val.destination_location_request_id.code
		no = self.pool.get('ir.sequence').get(cr, uid, 'pembelian.barang') + 'PB/SBM/' + code + '/' + time.strftime('%y') + '/' + time.strftime('%m')
		return self.write(cr,uid,ids,{'state':'confirm','name':no},context=context)

	def edit(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'edit'})

	def setdraft(self,cr,uid,ids,context={}):
		context.update(action_state='draft')
		# print '============',data
		return self.write(cr,uid,ids,{'state':'draft'},context=context)

	def confirm3(self,cr,uid,ids,context={}):
		val = self.browse(cr, uid, ids)[0]
		obj_detail_pb=self.pool.get('detail.pb')
		for detail in val.detail_pb_ids:
			if detail.state == 'draft':
				cr.execute('Update detail_pb Set state=%s Where id=%s', ('onproses',detail.id))
		return self.write(cr,uid,ids,{'state':'purchase'})

	def confirm(self,cr,uid,ids,context={}):
#		val = self.browse(cr, uid, ids)[0]
#		usermencet = self.pool.get('res.user')
#		if val.employee_id.parent_id.id != uid :
#			raise osv.except_osv(('Perhatian..!!'), ('Harus Atasannya langsung ..'))
		context.update(action_state='confirm')
		return self.write(cr,uid,ids,{'state':'confirm2'},context=context)

	def confirm2(self,cr,uid,ids,context={}):
#		val = self.browse(cr, uid, ids)[0]
#		usermencet = self.pool.get('res.user')
#		if val.employee_id.parent_id.id != uid :
#			raise osv.except_osv(('Perhatian..!!'), ('Harus Atasannya langsung ..'))
		context.update(action_state='confirm2')
		cr.execute('Update detail_pb Set state=%s Where detail_pb_id=%s', ('onproses',ids[0]))
		return self.write(cr,uid,ids,{'state':'purchase'},context=context)

	def purchase(self,cr,uid,ids,context={}):
		return self.write(cr,uid,ids,{'state':'done'})


	def reportpb(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		datas = {'ids': context.get('active_ids', [])}
		datas['model'] = 'pembelian.barang'
		datas['form'] = self.read(cr, uid, ids)[0]
		
		return {
			'type': 'ir.actions.report.xml',
			'report_name': 'print.pb',
			'report_type': 'webkit',
			'datas': datas,
			}

Pembelian_Barang()


class ClassName(osv.osv):
	
	def action_cancel_item(self,cr,uid,ids,context=None):
		if context is None:
			context = {}
		
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_purchase', 'wizard_pr_cancel_form')

		# print "<<<<<<<<<<<<<<<<<<<<",view_id

		context.update({
			'active_model': self._name,
			'active_ids': ids,
			'active_id': len(ids) and ids[0] or False
		})
		return {
			'view_mode': 'form',
			'view_id': view_id,
			'view_type': 'form',
			'view_name':'wizard_pr_cancel_form',
			'res_model': 'wizard.pr.cancel.item',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
			'nodestroy': True,
		}

	_inherit = 'pembelian.barang'



class WizardPRCancelItem(osv.osv_memory):
	
	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		pb_ids = context.get('active_ids', [])
		# print '====================',pb_ids
		active_model = context.get('active_model')
		res = super(WizardPRCancelItem, self).default_get(cr, uid, fields, context=context)
		if not pb_ids or len(pb_ids) != 1:
			# Partial Picking Processing may only be done for one picking at a time
			return res
		pb_id, = pb_ids
		if pb_id:
			res.update(pb_id=pb_id)
			pb = self.pool.get('pembelian.barang').browse(cr, uid, pb_id, context=context)
			# linesData = []
			# linesData += [self._load_po_line(cr, uid, l) for l in po.order_line if l.state not in ('done','cancel')]
			# res.update(lines=linesData)
		print res,",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
		return res


	def request_cancel(self,cr,uid,ids,context=None):
		print "CALLING request_cancel_item method"
		data = self.browse(cr,uid,ids,context)[0]

		lines = self.pool.get('detail.pb').search(cr, uid, [('detail_pb_id', '=', data.pb_id.id)])
		dp = self.pool.get('detail.pb').browse(cr, uid, lines)
		for x in dp:
			self.pool.get('detail.pb').write(cr,uid,x.id,{'state':'cancel'})
			
		return self.pool.get('pembelian.barang').write(cr,uid,data.pb_id.id,{'cancel_reason':data.cancel_reason,'state':'cancel'})


	_name="wizard.pr.cancel.item"
	_description="Wizard Cancel Item On PR"
	_columns = {
		'pb_id':fields.many2one('pembelian.barang',string="Purchase Requisition",required=True),
		'cancel_reason':fields.text('Cancel Reason',required=True,help="Reason why item(s) want to be cancel"),
	}

	_rec_name="pb_id"


WizardPRCancelItem()


class Detail_PB(osv.osv):
	STATES = [
		('draft', 'Draft'),
		('onproses', 'Confirm'),
		('proses','Proses'),
		('done', 'Done'),
		('cancel', 'Cancel')
	]

	def _get_processed_items(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			move=self.pool.get('purchase.order.line').search(cr,uid,[('line_pb_general_id', '=' ,item.id),('state', 'in' ,['confirmed','done'])])
			hasil= 0
			for data in  self.pool.get('purchase.order.line').browse(cr,uid,move):
				# hasil += data.received_items
				hasil += data.product_qty
			res[item.id] = hasil
		return res

	def _get_qty_available(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			move=self.pool.get('purchase.order.line').search(cr,uid,[('line_pb_general_id', '=' ,item.id),('state', 'in' ,['confirmed','done'])])
			hasil= 0
			for data in  self.pool.get('purchase.order.line').browse(cr,uid,move):
				hasil += data.product_qty
			nilai =item.jumlah_diminta-hasil

			res[item.id] = nilai
			if item.state=="proses":
				if nilai <> 0:
					self.write(cr,uid,ids,{'state':'onproses'})
		return res

	def _get_cek_po_line(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
			result[line.line_pb_general_id.id] = True
		return result.keys()

	def _get_cek_detail_pb(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('detail.pb').browse(cr, uid, ids, context=context):
			result[line.id] = True
		return result.keys()


	def _get_delivery_items(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			move=self.pool.get('order.requisition.delivery.line').search(cr,uid,[('purchase_requisition_line_id', '=' ,item.id),('state', '=' ,'done')])
			hasil= 0
			for data in  self.pool.get('order.requisition.delivery.line').browse(cr,uid,move):
				hasil += data.qty_delivery
			res[item.id] = hasil
		return res

	def _get_cek_delivery_item(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('order.requisition.delivery.line').browse(cr, uid, ids, context=context):
			result[line.purchase_requisition_line_id.id] = True
		return result.keys()




	# FOR STATE FIELD
	def _getParentState(self,cr,uid,ids,field_name,args,context={}):
		res = {}
		for data in self.browse(cr,uid,ids,context):
			
			move=self.pool.get('order.requisition.delivery.line').search(cr,uid,[('purchase_requisition_line_id', '=' ,data.id),('state', '=' ,'done')])
			hasil= 0
			for x in  self.pool.get('order.requisition.delivery.line').browse(cr,uid,move):
				hasil += x.qty_delivery

			po_line=self.pool.get('purchase.order.line').search(cr,uid,[('line_pb_general_id', '=' ,data.id),('state', 'in' ,['confirmed','done'])])
			Available= 0
			nilai =0
			for y in  self.pool.get('purchase.order.line').browse(cr,uid,po_line):
				Available += y.product_qty
			nilai =data.jumlah_diminta-Available

			if data.state == "draft":
				res[data.id] = "draft"
			elif data.jumlah_diminta==hasil and data.state=="proses":
				res[data.id] = "done"
			elif nilai == 0.0 and data.state=="onproses":
				res[data.id] = "proses"
			elif nilai > 0 and data.state=="onproses":
				res[data.id] = "onproses"
		return res


	def _get_cek_state_detail_pb(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('order.requisition.delivery.line').browse(cr, uid, ids, context=context):
			result[line.purchase_requisition_line_id.id] = True
		return result.keys()


	def _get_cek_state_po_line(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
			result[line.line_pb_general_id.id] = True
		return result.keys()

	_name = 'detail.pb'
	_columns = {
		'name':fields.many2one('product.product','Product',track_visibility='onchange'),
		'variants':fields.many2one('product.variants','variants',track_visibility='onchange'),
		'part_no':fields.char('Part No',track_visibility='onchange'),
		'jumlah_diminta':fields.float('Qty',track_visibility='onchange'),
		'satuan':fields.many2one('product.uom','Product UOM',track_visibility='onchange'),
		'stok':fields.integer('Stock',track_visibility='onchange'),
		'customer_id':fields.many2one('res.partner','Customer', domain=[('customer','=',True)]),
		'harga':fields.float('Unit Price'),
		'subtotal':fields.float('Sub Total'),
		'keterangan':fields.text('Keterangan'),
		'detail_pb_id':fields.many2one('pembelian.barang', 'Referensi PB', required=True, ondelete='cascade'),
		'item': fields.many2many('set.po', 'pre_item_rel', 'permintaan_id', 'item_id', 'item'),
		'sale_line_ids':fields.many2one('sale.order.line','SaleId'),
		'qty_available': fields.function(_get_qty_available,string="Qty Available",type="float", readonly=False, track_visibility='always',
			store={
				'detail.pb': (lambda self, cr, uid, ids, c={}: ids, ['detail_pb_id'], 20),
				'purchase.order.line': (_get_cek_po_line, ['state'], 20),
			}),
		'delivery_items': fields.function(_get_delivery_items,string="Received Items",type="float",
			store={
				'detail.pb': (lambda self, cr, uid, ids, c={}: ids, ['detail_pb_id'], 20),
				'order.requisition.delivery.line':(_get_cek_delivery_item,['state'],20),
			}),
		'processed_items': fields.function(_get_processed_items,string="Processed Items",type="float",store=False),
		'state':fields.function(_getParentState,method=True,string="State",type="selection",selection=STATES,
			store={
				'detail.pb': (lambda self, cr, uid, ids, c={}: ids, ['detail_pb_id'], 20),
				'order.requisition.delivery.line': (_get_cek_state_detail_pb, ['state'], 20),
				'purchase.order.line': (_get_cek_state_po_line, ['state'], 20),
			}),
	}

	_defaults = {'state': 'draft'}


	def cekproduct(self,cr,uid,ids,qty_available,jumlah_diminta):
		if jumlah_diminta>qty_available:
			res = {
				'value':{
					'quantity':qty_available,
				},
				'warning':{
					'title':'Qty Not Valid',
					'message':'Qty not Enough!'
				}
			}
		else:
			res = {
				'value':{
					'quantity':jumlah_diminta,
				},
			}
		return res


	def onchange_product_new(self, cr, uid, ids, name, satuan, context=None):
		if name:
			product_id =self.pool.get('product.product').browse(cr,uid,name)
			if product_id.categ_id.id == 105:
				uom=satuan
			else:
				uom=product_id.uom_id.id
		else:
			uom=1
		return {'value':{'satuan':uom}}

	def setvariants(self,cr,uid,ids, pid):
		if pid:
			cek=self.pool.get('product.variants').search(cr,uid,[('product_id', '=' ,pid)])
			hasil=self.pool.get('product.variants').browse(cr,uid,cek)
			products=self.pool.get('product.product').browse(cr,uid,pid)
			pn = products.default_code
			product =[x.id for x in hasil]
			return {'domain': {'variants': [('id','in',tuple(product))]},'value':{'part_no':pn,'stok':products.qty_available,'satuan':products.uom_id.id}}

	def productvar(self,cr,uid,ids,idp):
		hasil=self.pool.get('product.variants').browse(cr,uid,idp)
		return {'value':{ 
						'part_no':hasil.default_code,
						'stok':hasil.qty_available,
						'satuan':hasil.uom_id.id,
						} }

	def jmlQty(self,cr,uid,ids, qty):
		return {'value':{ 
						'qty_available':qty} }

Detail_PB()

class Type_PB(osv.osv):
	_name = 'type.pb'
	_columns= {
		'name' : fields.char('Type Permintaan'),
	}
		
Type_PB()

class Set_PO(osv.osv):
	_name = 'set.po'
	_columns ={
		'name':fields.many2one('res.partner','Supplier',required=True, domain=[('supplier','=',True),('is_company', '=', True)]),
		'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', required=True, domain=[('type','=','purchase')]),
		'order_type':fields.selection([('1','Normal Order'),('2','Petty Order')],'Order Type',required=True),
		'permintaan': fields.many2many('detail.pb', 'pre_item_rel', 'item_id', 'permintaan_id', 'Detail Permintaan',domain=[('state','=','onproses'),('qty_available','>',0)]),
	}
	
	_defaults = {
		'order_type': 1,
	}
	def create_po(self,cr,uid,ids,fiscal_position_id=False,context=None):
		val = self.browse(cr, uid, ids)[0]
		# Perhitangan Pajak
		account_fiscal_position = self.pool.get('account.fiscal.position')
		account_tax = self.pool.get('account.tax')

		obj_purchase = self.pool.get("purchase.order")
		obj_purchase_line = self.pool.get('purchase.order.line')
		obj_detail_order_line=self.pool.get('detail.order.line')
		obj_wizard_detail=self.pool.get('wizard.detail.pb');


		pb = [line.detail_pb_id.name for line in val.permintaan]
		detailpb = ''
		for x in set(pb):
			detailpb += x[:5] + ', '

		
		if val.order_type == 1 :
			jenis = 'loc'
			seq =int(time.time())
		else:
			jenis = 'loc-petty'
			seq =int(time.time())
			
		sid = obj_purchase.create(cr, uid, {
										'name':seq,
										'date_order': time.strftime("%Y-%m-%d"),
										'duedate':time.strftime("%Y-%m-%d"),
										'partner_id': val.name.id,
										'jenis': jenis,
										'pricelist_id': val.pricelist_id.id,
										'location_id': 12,
										'origin':detailpb,
										'type_permintaan':'1',
										'term_of_payment':val.name.term_payment
									   })
		noline=1
		for line in val.permintaan:
			taxes = account_tax.browse(cr, uid, map(lambda line: line.id, line.name.supplier_taxes_id))
			fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
			taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
			print "Callling PO Line Create----------------------"
			obj_purchase_line.create(cr, uid, {
										 'no':noline,
										 'date_planned': time.strftime("%Y-%m-%d"),
										 'order_id': sid,
										 #'pb_id': products[line]['name'],
										 # 'pb_id': line.detail_pb_id.id,
										 'product_id': line.name.id,
										 'variants':line.variants.id,
										 'name':line.name.name,
										 'part_number':line.name.default_code,
										 'line_pb_general_id': line.id,
										 'product_qty': line.qty_available,
										 'product_uom': line.satuan.id,
										 'price_unit': line.harga,
										 'note_line':'-',
										 'taxes_id': [(6,0,taxes_ids)],
										 })
			noline=noline+1
			print '===================TEST NO====================',noline

		# purchase ==> Nama Module nya purchase_order_form ==> Nama Id Form nya
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
		action['res_id'] = sid
		return action

Set_PO()

# class Search_PB(osv.osv_memory):
# 	_name = 'search.pb'
# 	_columns={
# 		'name':fields.many2many('detail.pb','search_pb_rel','search_detail_pb','id'),
# 	}

class Wizard_Detail_PB(osv.osv):
	_name = 'wizard.detail.pb'
	_columns ={
		'name':fields.many2one('pembelian.barang','No PB', domain=[('state','=','purchase')]),
		'product':fields.many2one('product.product','Product'),
		'variants':fields.many2one('product.variants','variants'),
		'jumlah_diminta':fields.integer('Qty'),
		'qty_available':fields.integer('Qty Available'),
		'price_unit':fields.integer('Price Unit', required=True),
		'id_product_detail':fields.integer('id'),
		'detail_pb_id':fields.many2one('set.po', 'Detail PO', required=True, ondelete='cascade'),
		# 'detail_pb_ids': fields.many2many('detail.pb', 'detail_set_pb', 'Detail Permintaan Barang'),
	}
	

	def cekproduct(self,cr,uid,ids,qty_available,jumlah_diminta):
		if jumlah_diminta>qty_available:
			res = {
				'value':{
					'quantity':qty_available,
				},
				'warning':{
					'title':'Qty Not Valid',
					'message':'Qty not Enough!'
				}
			}
		else:
			res = {
				'value':{
					'quantity':jumlah_diminta,
				},
			}
		return res


	def setProduct(self,cr,uid,ids, pid):
		pb_id = self.pool.get('pembelian.barang').browse(cr,uid, pid)
		cek=self.pool.get('detail.pb').search(cr,uid,[('detail_pb_id', '=' ,pb_id.id),('state', '=' ,'onproses')])
		#product =[x.name.id for x in pb_id.detail_pb_ids]
		hasil=self.pool.get('detail.pb').browse(cr,uid,cek)
		product =[x.name.id for x in hasil]
		return {'domain': {'product': [('id','in',tuple(product))]}}
	
	def setQty(self,cr,uid,ids, pid, pb):
		pb_id = self.pool.get('pembelian.barang').browse(cr,uid, pb) 
		pb_product = self.pool.get('pembelian.barang').browse(cr,uid, pid)
		cek=self.pool.get('detail.pb').search(cr,uid,[('detail_pb_id', '=' ,pb_id.id),('name', '=' ,pid)])
		hasil=self.pool.get('detail.pb').browse(cr,uid,cek)[0]
		return {'value':{ 'qty':hasil.qty_available, 'id_product_detail':hasil.id} }

Wizard_Detail_PB()


class Detail_Order_Line(osv.osv):
	_name = 'detail.order.line'
	_columns = {
		'name':fields.integer('Id'),
		'order_line_id':fields.integer('Id Order Line'),
		'detail_pb_id':fields.integer('Id Detail PB'),
		'qty':fields.float('Qty'),
	}

Detail_Order_Line()


class Product_Variants(osv.osv):
	_name = 'product.variants'
	_columns = {
		# 'name':fields.integer('variants_id'),
		'product_id':fields.many2one('product.product','Product'),
		'name':fields.char('Variants'),
		'satuan':fields.many2one('product.uom','Product UOM'),
	}

Product_Variants()