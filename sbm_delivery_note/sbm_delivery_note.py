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

	def _is_filter_years(self,cr,uid,ids,field_name,arg,context={}):
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			if item.name <> '/':
				dn_no = item.name[-2:]
				res[item.id] = {'data_years':float(dn_no)}
		return res

	def _get_years(self,cr,uid,ids,field_name,arg,context={}):

		return True


	def _get_month(self,cr,uid,ids,field_name,arg,context={}):

		return True


	def _search_month(self, cr, uid, obj, name, args, context):
		for x in args:
			filter_no=str(x[2])
			month = '0'
			if filter_no == '1':
				month = 'I'
			elif filter_no == '2':
				month = 'II'
			elif filter_no == '3':
				month = 'III'
			elif filter_no == '4':
				month = 'IV'
			elif filter_no == '5':
				month = 'V'
			elif filter_no == '6':
				month = 'VI'
			elif filter_no == '7':
				month = 'VII'
			elif filter_no == '8':
				month = 'VIII'
			elif filter_no == '9':
				month = 'IX'
			elif filter_no == '10':
				month = 'X'
			elif filter_no == '11':
				month = 'XI'
			elif filter_no == '12':
				month = 'XII'
		res = [('name','like','%/%/%/'+month+"/%")]
		return res

	def _search_years(self, cr, uid,obj, name, args, context={}):
		for x in args:
			filter_no = str(x[2])
			if len(filter_no)>2:
				filter_no=filter_no[-2:]
		res = [('name','ilike','%/'+str(filter_no))]
		return res

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
		'data_years':fields.function(_is_filter_years, store=True, string="Years Delivery Note", multi="data_years"),
		'doc_year':fields.function(_get_years,fnct_search=_search_years,string='Doc Years',store=False),
		'doc_month':fields.function(_get_month,fnct_search=_search_month,string='Doc Month',store=False),
	}

	_order = "id desc"



	def print_dn_out_new(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"delivery-note/printnew&id="+str(ids[0])+"&uid="+str(uid)
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'print.int.move',
			'params': {
				'redir'	: urlTo,
				'uid':uid
			},
		}

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
				# Jika OP merupakan OP Lama
				line_op = self.pool.get('order.preparation.line').search(cr, uid, [('preparation_id', '=', pre)])
				for op_line in self.pool.get('order.preparation.line').browse(cr,uid,line_op):
					
					material_line = []

					material_line.append((0,0,{
						'name':op_line.product_id.id,
						'desc':op_line.name,
						'qty':op_line.product_qty,
						'product_uom':op_line.product_uom.id,
						'op_line_id':op_line.id
					}))

					line.append({
						'no': op_line.no,
						'product_id' : op_line.product_id.id,
						'product_qty': op_line.product_qty,
						'product_uom': op_line.product_uom.id,
						'name': op_line.name,
						'note_lines_material': material_line
					})

				# raise openerp.exceptions.Warning("Order Preparation Tidak Memiliki Material Lines")

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
										'location_id':dline.picking_location.id,
										'op_line_id':dopline.id
									}))
							else:
								material_line.append((0,0,{
									'name':dopline.product_id.id,
									'desc':dopline.name,
									'qty':dopline.product_qty,
									'product_uom':dopline.product_uom.id,
									'location_id':dline.picking_location.id,
									'op_line_id':dopline.id
									}))
				line.append({
					'no': y.sequence,
					'product_id' : y.product_id.id,
					'product_qty': qty_dn_line,
					'product_uom': y.product_uom.id,
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


	def get_sequence_no(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		dn = self.pool.get('delivery.note')
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

		return dn.write(cr,uid,val.id,{'name':dn_no})


	def generate_no(self, cr, uid, ids, context=None):

		return self.pool.get('delivery.note').get_sequence_no(cr, uid, ids)


	def create_picking(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		dn = self.pool.get('delivery.note')
		stock_picking = self.pool.get('stock.picking')
		stock_location = self.pool.get('stock.location')
		stock_move = self.pool.get('stock.move')
		dn_material = self.pool.get('delivery.note.line.material')

		picking_type = 'out'
		seq_obj_name =  'stock.picking.' + picking_type

		m  = self.pool.get('ir.model.data')
		id_loc = m.get_object(cr, uid, 'stock', 'stock_location_customers').id

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
				if x.location_id.id:
					loc_id =x.location_id.id
				else:
					loc_id = 12

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
					'location_id' :loc_id,
					'company_id':1,
					'picking_id': picking,
					'state':'draft',
					'location_dest_id' :id_loc
					},context=context)
				

				print '================',move_id
				# Update DN Line Material Dengan ID Move
				dn_material.write(cr,uid,x.id,{'stock_move_id':move_id})

		# Update Picking id di DN
		dn.write(cr,uid,val.id,{'picking_id':picking})

		stock_picking.action_assign(cr, uid, [picking])

		return True


	def approve_note(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		dn = self.pool.get('delivery.note')
		dn_line = self.pool.get('delivery.note.line')
		dn_material = self.pool.get('delivery.note.line.material')
		stock_picking = self.pool.get('stock.picking')
		stock_move = self.pool.get('stock.move')


		cek = dn_line.search(cr,uid, [('note_id','=', ids)])
		hasil = dn_line.browse(cr, uid, cek)
		for data in hasil:
			product =[x.id for x in data.note_lines_material if x.id]
			if product == []:
				raise openerp.exceptions.Warning("Delivery Note Line Tidak Memiliki Material Lines")

		# Jalankan Fungsi Asli Package Confirm
		dn.package_confirm(cr,uid, ids)

		# Jalankan Fungsi Sequence No
		dn.get_sequence_no(cr, uid, ids)

		# Jalankan Fungsi Create Picking
		dn.create_picking(cr, uid, ids)

		return True

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

		if val.picking_id.id == False:
			raise openerp.exceptions.Warning("Delivery Note Tidak Dapat di Postpone")


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
		if val.picking_id.id:
			stock_picking = self.pool.get('stock.picking')
			stock_move = self.pool.get('stock.move')
			partial_data = {}
			move = self.pool.get('stock.move').search(cr, uid, [('picking_id', '=', val.picking_id.id)])
			data_move = self.pool.get('stock.move').browse(cr, uid, move)
			# Update Done Picking & Move
			stock_picking.action_move(cr, uid, [val.picking_id.id])

			self.write(cr, uid, ids, {'state': 'done'})
		else:
			self.pool.get('delivery.note').package_validate(cr, uid, ids)
			self.write(cr, uid, ids, {'picking_id': val.prepare_id.picking_id.id})
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


	def return_product(self, cr, uid, ids, context=None):
		res = {}
		val = self.browse(cr, uid, ids)[0]
		dn = self.pool.get('delivery.note')

		if val.picking_id.id:
			dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'view_stock_return_picking_form')
			res = {
				'name':'Return Shipment',
				'view_mode': 'form',
				'view_id': view_id,
				'view_type': 'form',
				'view_name':'stock.stock_return_picking_memory',
				'res_model': 'stock.return.picking.memory',
				'type': 'ir.actions.act_window',
				'target': 'new',
				'res_id':val.picking_id.id,
				'domain': "[('id','=',"+str(val.picking_id.id)+")]",
				'key2':'client_action_multi',
				'multi':"True",
				'context':{
					'active_id':val.picking_id.id,
					'active_model':'stock.return.picking',
					'active_ids':val.picking_id.id,
				}
			}
			if val.picking_id.id==False:
				dn.write(cr,uid,val.id,{'picking_id':val.prepare_id.picking_id.id})
		else:
			res = super(delivery_note,self).return_product(cr,uid,ids,context={})

		return res


delivery_note()


class packing_list_line(osv.osv):
	_inherit = "packing.list.line"


	def refresh(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]
		if val.picking_id.id:
			for y in val.note_id.note_lines:
				for x in y.note_lines_material:
					res = self.pool.get('product.list.line').create(cr, uid, {
																  'no': y.no,
																  'name': x.name,
																  'packing_id': val.id,
																  'product_id': x.name.id,
																  'product_qty': x.qty,
																  'product_uom': x.product_uom.id,
																  # 'product_packaging': y.note_id.product_packaging.id,
																  })
		else:
			res = super(packing_list_line,self).refresh(cr,uid,ids,context={})

		return res


packing_list_line()


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
		'state':fields.related('note_id', 'state', type='selection', store=False, string='State'),
		'note_lines_material': fields.one2many('delivery.note.line.material', 'note_line_id', 'Note Lines Material', readonly=False),
	}

	def onchange_product_id(self, cr, uid, ids, product_id, uom_id):
		product = self.pool.get('product.template').browse(cr, uid, product_id)

		uom = uom_id

		if product_id:
			if uom_id == False:
				uom = product.uom_id.id
			else:
				if uom_id == product.uom_id.id:
					uom = product.uom_id.id
				elif uom_id == product.uos_id.id:
					uom = product.uos_id.id
				elif uom_id <> product.uom_id.id or uom_id <> product.uos_id.id:
					uom = product.uom_id.id
				else:
					uom = False
					raise openerp.exceptions.Warning('UOM Error')
		return {'value':{'product_uom':uom}}

delivery_note_line()


class delivery_note_line_material(osv.osv):

	def _get_refunded_item(self,cr,uid,ids,field_name,arg,context={}):
		res = {}
		for item in self.browse(cr,uid,ids,context=context):
			refunded_total = 0
			for refund in item.note_line_material_return_ids:
				refunded_total += refund.product_qty

			if item.qty == refunded_total:
				self.write(cr,uid,[item.id],{'state':'donerefund'})
			res[item.id] = refunded_total
		return res


	_name = "delivery.note.line.material"
	_columns = {
		'name': fields.text('Description'),
		'product_id' : fields.many2one('product.product',required=True, string="Product"),
		'prodlot_id':fields.many2one('stock.production.lot','Serial Number'),
		'note_line_id': fields.many2one('delivery.note.line', 'Delivery Note Line', required=True, ondelete='cascade'),
		'qty': fields.float('Qty',required=True),
		'product_uom': fields.many2one('product.uom',required=True, string='UOM'),
		'stock_move_id': fields.many2one('stock.move',required=False, string='Stock Move'),
		'desc': fields.text('Description',required=False),
		'location_id':fields.many2one('stock.location',required=False),
		'op_line_id':fields.many2one('order.preparation.line','OP Line',required=False),
		'note_line_material_return_ids': fields.many2many('stock.move','delivery_note_line_material_return','delivery_note_line_material_id',string="Note Line Material Returns"),
		'refunded_item': fields.function(_get_refunded_item, string='Refunded Item', store=False),
		'state': fields.related('note_line_id','state', type='many2one', relation='delivery.note.line', string='State'),
	}

delivery_note_line_material()



class order_preparation_line(osv.osv):
	_inherit = "order.preparation.line"
	_columns = {
		'dn_line_materials':fields.one2many('delivery.note.line.material','op_line_id', string='DN Materail', required=False),
	}

order_preparation_line()



class delivery_note_line_material_return(osv.osv):
	_name = 'delivery.note.line.material.return'	
	_columns = {
		'id':fields.integer('ID'),
		'delivery_note_id': fields.many2one('delivery.note','Delivery Note', ondelete='cascade',onupdate="cascade"),
		'delivery_note_line_id': fields.many2one('delivery.note.line','Delivery Note Line',ondelete='cascade',onupdate="cascade"),
		'delivery_note_line_material_id': fields.many2one('delivery.note.line.material','Delivery Note Line Material',ondelete='cascade',onupdate="cascade"),
		'stock_picking_id': fields.many2one('stock.picking','Stock Picking',ondelete='cascade',onupdate="cascade"),
		'stock_move_id': fields.many2one('stock.move','Stock Move',ondelete='cascade', onupdate="cascade"),
	}

delivery_note_line_material_return()



class stock_picking(osv.osv):
	_name = 'stock.picking'
	_inherit = ["stock.picking","mail.thread"]
	_columns = {
		'is_postpone': fields.boolean('Is Postpone'),
	}

stock_picking()


class stock_return_picking(osv.osv_memory):
	_inherit = 'stock.return.picking'
	_name = 'stock.return.picking'
	_description = 'Return Picking'


	def default_get(self, cr, uid, fields, context=None):

		result1 = []
		if context is None:
			context = {}
		res = super(stock_return_picking, self).default_get(cr, uid, fields, context=context)

		record_idx = context and context.get('active_id', False) or False

		if context.get('active_model') == 'stock.picking' or context.get('active_model') =='stock.picking.in' or context.get('active_model') =='stock.picking.out':
			record_id = context and context.get('active_id', False)
		else:
			val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)

			if val.picking_id.id:
				record_id = val.picking_id.id
			else:
				record_id = val.prepare_id.picking_id.id
				

		pick_obj = self.pool.get('stock.picking')
		pick = pick_obj.browse(cr, uid, record_id, context=context)
		if pick:
			if 'invoice_state' in fields:
				if pick.invoice_state=='invoiced':
					res.update({'invoice_state': '2binvoiced'})
				else:
					res.update({'invoice_state': 'none'})
			return_history = self.get_return_history(cr, uid, record_id, context)       
			for line in pick.move_lines:
				qty = line.product_qty - return_history.get(line.id, 0)
				if qty > 0:
					result1.append({'product_id': line.product_id.id, 'sisa':qty, 'quantity': qty,'move_id':line.id, 'prodlot_id': line.prodlot_id and line.prodlot_id.id or False})

			if 'product_return_moves' in fields:
				res.update({'product_return_moves': result1})

		return res


	def view_init(self, cr, uid, fields_list, context=None):

		res ={}
		if context is None:
			context = {}
		record_idx = context and context.get('active_id', False)
		if context.get('active_model') == 'stock.picking' or context.get('active_model') == 'stock.picking.in' or context.get('active_model') == 'stock.picking.out':
			record_id = context and context.get('active_id', False)
		else:
			val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)

			if val.picking_id.id:
				record_id = val.picking_id.id
				context.update({
					'active_model': 'stock.picking',
					'active_ids': [val.picking_id.id],
					'active_id': val.picking_id.id
				})
			else:
				record_id = val.prepare_id.picking_id.id
				context.update({
					'active_model': 'stock.picking',
					'active_ids': [val.prepare_id.picking_id.id],
					'active_id': val.prepare_id.picking_id.id
				})
		res = super(stock_return_picking, self).view_init(cr, uid, fields_list, context=context)
		return res


	def get_return_history(self, cr, uid, pick_id, context=None):
		
		return super(stock_return_picking, self).get_return_history(cr, uid, pick_id, context=context)


	def create_returns(self, cr, uid, ids, context=None):
		dn = self.pool.get('delivery.note')
		# call active dn
		active_dn_id = context['active_ids'][0]
		dn_obj = dn.browse(cr,uid,context['active_ids'][0],context=context)


		if context is None:
			context = {} 
		record_idx = context and context.get('active_id', False) or False
		
		val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)

		if context.get('active_model') == 'stock.picking' or context.get('active_model') == 'stock.picking.in' or context.get('active_model') == 'stock.picking.out':
			record_id = context and context.get('active_id', False) or False
		else:
			if val.picking_id.id:
				record_id = val.picking_id.id
			else:
				record_id = val.prepare_id.picking_id.id


		move_obj = self.pool.get('stock.move')
		pick_obj = self.pool.get('stock.picking')
		uom_obj = self.pool.get('product.uom')
		data_obj = self.pool.get('stock.return.picking.memory')
		act_obj = self.pool.get('ir.actions.act_window')
		model_obj = self.pool.get('ir.model.data')
		#  Delivery Note
		del_note = self.pool.get('delivery.note')

		wf_service = netsvc.LocalService("workflow")
		
		if context.get('active_model') == 'stock.picking' or context.get('active_model') == 'stock.picking.in' or context.get('active_model') == 'stock.picking.out':
			record_id = context and context.get('active_id', False) or False
			pick = pick_obj.browse(cr, uid, record_id, context=context)
		else:
			if val.picking_id.id:
				pick = pick_obj.browse(cr, uid, val.picking_id.id, context=context)
			else:
				pick = pick_obj.browse(cr, uid, val.prepare_id.picking_id.id, context=context)

		data = self.read(cr, uid, ids[0], context=context)
		date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
		set_invoice_state_to_none = True
		returned_lines = 0
		
		#Create new picking for returned products
		seq_obj_name = 'stock.picking'
		new_type = 'internal'
		if pick.type =='out':
			new_type = 'in'
			seq_obj_name = 'stock.picking.in'
		elif pick.type =='in':
			new_type = 'out'
			seq_obj_name = 'stock.picking.out'
		new_pick_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
		
		if context.get('active_model') == 'stock.picking' or context.get('active_model') ==  'stock.picking.in' or context.get('active_model') == 'stock.picking.out':
			new_picking = pick_obj.copy(cr, uid, pick.id, {
								'name': _('%s-%s-return') % (new_pick_name, pick.name),
								'move_lines': [], 
								'state':'draft', 
								'type': new_type,
								'date':date_cur,
								'invoice_state': data['invoice_state'],
								})
		else:
			new_picking = pick_obj.copy(cr, uid, pick.id, {
								'name': _('%s-%s-return') % (new_pick_name, pick.name),
								'move_lines': [], 
								'state':'draft', 
								'type': new_type,
								'date':date_cur,
								'note_id':val.id,
								'invoice_state': data['invoice_state'],
								})
			if val.picking_id.id:
				if val.picking_id.id==False:
					dn.write(cr,uid,val.id,{'note_return_ids':[(4,new_picking)],'picking_id':val.prepare_id.picking_id.id})
				else:
					dn.write(cr,uid,val.id,{'note_return_ids':[(4,new_picking)]})
			else:
				dn.write(cr,uid,val.id,{'note_return_ids':[(4,new_picking)]})


		dn_return_rel = []
		val_id = data['product_return_moves']
		
		# prepare op / to get note line id
		if context.get('active_model') == 'delivery.note':
			op_line = self.pool.get('order.preparation.line')
			dn_line = self.pool.get('delivery.note.line')
			dn_line_material = self.pool.get('delivery.note.line.material')


		for v in val_id:
			data_get = data_obj.browse(cr, uid, v, context=context)
			mov_id = data_get.move_id.id

			# search op and dn
			if context.get('active_model') == 'delivery.note':
				val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)
				if val.picking_id.id:
					dn_line_material_id=dn_line_material.search(cr,uid,[('stock_move_id','=',[mov_id])],context=context)
					dn_line_id = dn_line.search(cr,uid,[('note_lines_material','=',dn_line_material_id[0])],context=context)[0]
					id_line_material = dn_line_material_id[0]

				else:
					# op_line_id = op_line.search(cr,uid,[('move_id','=',mov_id)],context=context)
					# dn_line_id = dn_line.search(cr,uid,[('op_line_id','=',op_line_id[0])],context=context)[0]
					
					dn_line_material_id=dn_line_material.search(cr,uid,[('stock_move_id','=',mov_id)],context=context)
					dn_line_id = dn_line.search(cr,uid,[('note_lines_material','=',dn_line_material_id[0])],context=context)[0]
					id_line_material = dn_line_material_id[0]

			if not mov_id:
				raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))

			# Cek Barang yang sisa & yang di input
			return_history = self.get_return_history(cr, uid, pick.id, context)
			
			qty = 0
			for line in pick.move_lines:
				qty += line.product_qty - return_history.get(line.id, 0)

			if context.get('active_model') == 'delivery.note':
				if data_get.quantity > qty:
					raise osv.except_osv(_('Warning !'), _("Product Qty Tidak Mencukupi"))
					
			new_qty = data_get.quantity
			move = move_obj.browse(cr, uid, mov_id, context=context)
			new_location = move.location_dest_id.id
			returned_qty = move.product_qty
			for rec in move.move_history_ids2:
				returned_qty -= rec.product_qty

			if returned_qty != new_qty:
				set_invoice_state_to_none = False
			if new_qty:
				returned_lines += 1
				new_move=move_obj.copy(cr, uid, move.id, {
											'product_qty': new_qty,
											'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
											'picking_id': new_picking, 
											'state': 'draft',
											'location_id': new_location, 
											'location_dest_id': move.location_id.id,
											'date': date_cur,
				})
				move_obj.write(cr, uid, [move.id], {'move_history_ids2':[(4,new_move)]}, context=context)
				
			if context.get('active_model') == 'delivery.note':
				val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)
				if val.picking_id.id:
					tpl = {'delivery_note_id':active_dn_id,'stock_picking_id':new_picking,'delivery_note_line_id':dn_line_id,'delivery_note_line_material_id':id_line_material,'stock_move_id':new_move}
					dn_return_rel.append(tpl)
				else:
					tpl = {'delivery_note_id':active_dn_id,'stock_picking_id':new_picking,'delivery_note_line_id':dn_line_id,'stock_move_id':new_move}
					dn_return_rel.append(tpl)

		if context.get('active_model') == 'delivery.note':
			val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)

			dn_r = self.pool.get('delivery.note.line.return')
			dn_rm = self.pool.get('delivery.note.line.material.return')
			# write into dn line rel

			if val.picking_id.id:
				for note_line_return in dn_return_rel:
					print '===============',note_line_return
					dn_rm.create(cr,uid,note_line_return)
					# a
			else:	
				# Create return Lama 
				for note_line_return in dn_return_rel:
					dn_r.create(cr,uid,note_line_return)
		if not returned_lines:
			raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

		if set_invoice_state_to_none:
			pick_obj.write(cr, uid, [pick.id], {'invoice_state':'none'}, context=context)
		wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
		pick_obj.force_assign(cr, uid, [new_picking], context)
		# update Delivery Note
		if context.get('active_model') == 'delivery.note':
			val = self.pool.get('delivery.note').browse(cr, uid, record_idx, context=context)
			del_note.write(cr, uid, val.id, {'state':'torefund','refund_id':new_picking}, context=context)

		model_list = {
				'out': 'stock.picking.out',
				'in': 'stock.picking.in',
				'internal': 'stock.picking',
		}
		return {
			'domain': "[('id', 'in', ["+str(new_picking)+"])]",
			'name': _('Returned Picking'),
			'view_type':'form',
			'view_mode':'tree,form',
			'res_model': model_list.get(new_type, 'stock.picking'),
			'type':'ir.actions.act_window',
			'context':context,
		}

stock_return_picking()
