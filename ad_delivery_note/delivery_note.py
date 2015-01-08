from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import openerp.exceptions
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class sale_order(osv.osv):
	_inherit = "sale.order"
	_columns = {
		'internal_notes': fields.text('Internal Notes'),
	}

	def manual_invoice(self, cr, uid, ids, context=None):
		""" create invoices for the given sales orders (ids), and open the form
			view of one of the newly created invoices
		"""
		mod_obj = self.pool.get('ir.model.data')
		wf_service = netsvc.LocalService("workflow")

		# create invoices through the sales orders' workflow
		inv_ids0 = set(inv.id for sale in self.browse(cr, uid, ids, context) for inv in sale.invoice_ids)
		for id in ids:
			wf_service.trg_validate(uid, 'sale.order', id, 'manual_invoice', cr)
		inv_ids1 = set(inv.id for sale in self.browse(cr, uid, ids, context) for inv in sale.invoice_ids)
		
		
		# determine newly created invoices
		new_inv_ids = list(inv_ids1 - inv_ids0)

		if not new_inv_ids:
			new_inv_ids = [self.action_invoice_create(cr, uid, ids, context)]
			
		res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
		res_id = res and res[1] or False,

		return {
			'name': _('Customer Invoices'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': [res_id],
			'res_model': 'account.invoice',
			'context': "{'type':'out_invoice'}",
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': new_inv_ids and new_inv_ids[0] or False,
		}
		
sale_order()


class stock_picking(osv.osv):
	def print_im_out(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"moves/print&id="+str(ids[0])+"&uid="+str(uid)
		
		
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'print.int.move',
			'params': {
				# 'id'	: ids[0],
				'redir'	: urlTo,
				'uid':uid
			},
		}
	def _checkSetProduct(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for id in ids:
			res[id]= 0;
		return res
	_name = 'stock.picking'
	_inherit = ["stock.picking","mail.thread"]
	_columns = {
		'note_id': fields.many2one('delivery.note','Delivery Note', select=True),
		'note': fields.text('Notes', states={'done':[('readonly', False)]}),
		# 'move_set_datas': fields.one2many('move.set.data', '', 'Note Lines', readonly=True, states={'draft': [('readonly', False)]}),
		'move_set_datas':fields.one2many('move.set.data','picking_id',string="Move Set"),
		'isset_set':fields.function(_checkSetProduct,store=True,method=True,string="Is Has Set",type="boolean"),
		'state': fields.selection([
			('draft', 'Draft'),
			('warehouse','Check Warehouse'),
			('settodraft','Set To Draft'),
			('cancel', 'Cancelled'),
			('auto', 'Waiting Another Operation'),
			('confirmed', 'Waiting Availability'),
			('assigned', 'Ready to Transfer'),
			('done', 'Transferred'),
			], 'Status', readonly=True, select=True, track_visibility='onchange', help="""
			* Draft: not confirmed yet and will not be scheduled until confirmed\n
			* Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
			* Waiting Availability: still waiting for the availability of products\n
			* Ready to Transfer: products reserved, simply waiting for confirmation.\n
			* Transferred: has been processed, can't be modified or cancelled anymore\n
			* Cancelled: has been cancelled, can't be confirmed anymore"""
		),
	}
	_defaults={
		'isset_set':False,
	}
	def splitMoveLineSet(self,cr,uid,vals,context=None):
		getMoves  = vals.get('move_lines')
		getMoves2 = []
		moveSet = []
		move_set_data_obj = self.pool.get('move.set.data')
		# print "<BEFOREEEE",getMoves
		for move in getMoves :
			# print move,"<<<<<<<<<<<<<<<<<<<<<<<<<\\n"
			moveData = move[2]
			pQty = moveData['product_qty']
			
			# print moveData['product_id']
			product = self.pool.get('product.product').browse(cr,uid,moveData['product_id'])
			# print product
			isHasBOM = False
			if product.bom_ids:
				isHasBOM = True
				
				move_set_id = move_set_data_obj.create(cr,uid,{
					'product_id':int(moveData['product_id']),
					'product_qty':float(moveData['product_qty']),
					'product_uom':int(moveData['product_uom']),
					'location_id':int(moveData['location_id']),
					'location_dest_id':int(moveData['location_dest_id']),
					'type':moveData['type'],
					'no':float(moveData['no']),
					'desc':moveData['desc'],
					'picking_id':moveData['picking_id'] or False,

				})
				print move_set_id,'-------------------rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr'
				moveSet.append(move_set_id)
				for component in product.bom_ids[0].bom_lines:
					res = [0,False]
					bla = {}
					# print component.product_id.name
					bla['product_id']       = component.product_id.id
					bla['product_qty']      = component.product_qty * pQty
					bla['product_uom']      = component.product_uom.id
					bla['location_id']      = moveData['location_id']
					bla['location_dest_id'] = moveData['location_dest_id']
					bla['type']             = moveData['type']
					bla['no']               = moveData['no']
					bla['name']             = "["+component.product.default_code+"] "+component.product_id.name
					bla['desc']             = "["+component.product.default_code+"] "+component.product_id.name
					bla['set_id']           = move_set_id
					bla['partner_id']		= moveData['partner_id']
					bla['product_uos']		= component.product_uom.id
					bla['product_uos_qty']	= component.product_qty * pQty
					# print bla
					# print '=========================='
					res.append(bla)
					# print '==========================',res
					getMoves2.append(res)
				# getMoves.remove(move)
				# getMoves.remove()
				
			else:
				getMoves2.append(move)
		# print getMoves

		vals['move_lines'] = getMoves2

		# return False
		stock_p_id = super(stock_picking, self).create(cr, uid, vals, context)
		# print moveSet
		if stock_p_id:
			for move_set_line in moveSet:
				self.pool.get('move.set.data').write(cr,uid,move_set_line,{'picking_id':stock_p_id})
				# print stock_p_id,'=============='
		return stock_p_id
		self.cleanSetProductMove(cr,uid,stock_p_id,context)






	def write(self,cr,uid,ids,vals,context=None):
		# print "CALLEDD"
		# print "CALLED WRITE",ids
		res = super(stock_picking,self).write(cr,uid,ids,vals,context)
		# self.cleanSetProductMove(cr,uid,ids,context)
		# print vals,"---INI",context
		return res
		

	def cleanSetProductMove(self,cr,uid,ids,context=None):
		pickings = self.browse(cr,uid,ids,context)
		setsIds = []
		moveObj = self.pool.get('stock.move')
		# print "CALLING CLENA SET PRODUCT MOVE"
		print ids
		for picking in pickings:
			# print pickings,"=============<"

			for move in picking.move_lines:
				# print move,"======================>"
				pSet = False
				pQty = move.product_qty
				# print "move aaaaa ",move
				if move.product_id.bom_ids:
					pSet = True
					# add move to move_set_data
					moveSetData = {
						'origin_move_id':move.id,
						'product_id':move.product_id.id,
						'product_qty':move.product_qty,
						'product_uom':move.product_uom.id,
						'type':move.type,
						'no':move.no,
						'desc':move.desc or move.name or False,
						'location_id':move.location_id.id,
						'location_dest_id':move.location_dest_id.id,
						'picking_id':move.picking_id.id,
						
					}
					# print moveSetData
					move_set_id = self.pool.get('move.set.data').create(cr,uid,moveSetData)
					# add move id to list for delete in last
					setsIds.append(move.id)

					# create new move objects from bom component
					if move.product_id.bom_ids[0].bom_lines :
						# print "HAS BOMMMMMM"
						for component in move.product_id.bom_ids[0].bom_lines :
							bla = {}
							bla['product_id']       = component.product_id.id
							bla['product_qty']      = component.product_qty * pQty
							bla['product_uom']      = component.product_uom.id
							bla['location_id']      = move.location_id.id
							bla['location_dest_id'] = move.location_dest_id.id
							bla['type']             = move.type
							bla['no']               = move.no
							bla['name']				= "["+component.product_id.default_code+"] "+component.product_id.name
							bla['desc']             = "["+component.product_id.default_code+"] "+component.product_id.name
							bla['set_id']           = move_set_id
							bla['picking_id']		= picking.id
							bla['sale_line_id']		= move.sale_line_id.id
							bla['purchase_line_id']	= move.purchase_line_id.id or False
							bla['partner_id']		= move.partner_id.id
							bla['product_uos_qty']	= component.product_qty * pQty
							bla['product_uos']		= component.product_uom.id

							moveNew = self.pool.get('stock.move').create(cr,uid,bla,context)
							# print moveNew,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<,"
					else:
						raise osv.except_osv(_('Error!'), _('Please Define Bill Of Material Data First For ',move.product_id.name))
			# delete move where product is has BOM
			# print setsIds
			self.pool.get('stock.move').unlink(cr,uid,setsIds,context)



	

	def create(self, cr, uid, vals, context=None):
		# print "VALSSSSS",vals
		# print "CONTEXT",context



		getMoves  = vals.get('move_lines')
		# print "GET MOVESSSSSS======================",getMoves
		if getMoves:
			getMoves2 = []
			moveSet = []
			move_set_data_obj = self.pool.get('move.set.data')
			# print "<BEFOREEEE",getMoves,"MOVEEEE:"
			for move in getMoves :
				# print move,"<<<<<<<<<<<<<<<<<<<<<<<<<\\n"
				moveData = move[2]
				pQty = moveData['product_qty']
				
				# print moveData['product_id']
				product = self.pool.get('product.product').browse(cr,uid,moveData['product_id'])
				# print product
				isHasBOM = False
				if product.bom_ids:
					isHasBOM = True
					newMoveSet = {}
					newMoveSet = {
						'product_id':int(moveData['product_id']),
						'product_qty':float(moveData['product_qty']),
						'product_uom':int(moveData['product_uom']),
						'location_id':int(moveData['location_id']),
						'location_dest_id':int(moveData['location_dest_id']),
						'type':moveData['type'],
						'no':float(moveData['no']),
						'desc':moveData['desc'] or moveData['name'] or False,
					}
					if 'picking_id' in moveData:
						newMoveSet['picking_id'] = moveData['picking_id'] or False

					move_set_id = move_set_data_obj.create(cr,uid,newMoveSet)
					print move_set_id,'-------------------'
					moveSet.append(move_set_id)
					for component in product.bom_ids[0].bom_lines:
						res = [0,False]
						bla = {}
						# print component.product_id.name
						bla['product_id']       = component.product_id.id
						bla['product_qty']      = component.product_qty * pQty
						bla['product_uom']      = component.product_uom.id
						bla['location_id']      = moveData['location_id']
						bla['location_dest_id'] = moveData['location_dest_id']
						bla['type']             = moveData['type']
						bla['no']               = moveData['no']
						bla['name']             = "["+component.product_id.default_code+"] "+component.product_id.name
						bla['desc']             = component.product_id.name
						bla['set_id']           = move_set_id
						if 'purchase_line_id' in moveData:
							bla['purchase_line_id']	= moveData['purchase_line_id']
						bla['product_uos']		= component.product_uom.id
						bla['product_uos_qty']	= component.product_qty * pQty
						# print bla
						# print '=========================='
						res.append(bla)
						# print '==========================',res
						getMoves2.append(res)
					# getMoves.remove(move)
					# getMoves.remove()
					
				else:
					getMoves2.append(move)
			# print getMoves

			vals['move_lines'] = getMoves2

			# return False
			stock_p_id = super(stock_picking, self).create(cr, uid, vals, context)
			# print moveSet
			if stock_p_id:
				for move_set_line in moveSet:
					self.pool.get('move.set.data').write(cr,uid,move_set_line,{'picking_id':stock_p_id})
					# print stock_p_id,'=============='
			return stock_p_id
			# return False
			# raise osv.except_osv(_('No Customer Defined!'), _('Tes'))
		else:
			# IF NOT FROM MOVES
			# print "THISSSSSSS"
			stock_p_id =  super(stock_picking,self).create(cr,uid,vals,context)
			# print "STOCK P ID",stock_p_id
			return stock_p_id
			# return False
		# return super(stock_picking,self).create(cr,uid,vals,context)


	def draft_force_warehouse(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids)[0]
		
		for x in val.move_lines:
			product =self.pool.get('product.product').browse(cr, uid, x.product_id.id)
			product = x.product_id
			# pQty = x.product_qty

			isHasBOM = False
			# if product is SET / HAS A BOM MATERIALS
			if product.bom_ids:
				# print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ADA BOM ",product.id
				isHasBOM = True
				line_bom = x.id
				# bom = product.bom_ids[0].bom_lines
				# LOOP EACH BOM
				# for component in product.bom_ids[0].bom_lines :
					# print ".....",component.product_id.name," ",component.product_qty," ",component.product_uom.name

			# CHECK PRODUCT AVAILABILITY
			print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',product.default_code
			if product.not_stock == False:
				mm = ' ' + product.default_code + ' '
				stock = ' ' + str(product.qty_available) + ' '
				msg = 'Stock Product' + mm + 'Tidak Mencukupi.!\n'+ ' On Hand Qty '+ stock 

				# UNCOMMENT THIS FOR LIVE
				if x.product_qty > product.qty_available:
					raise openerp.exceptions.Warning(msg)
					return False
				# END UNCOMMENT FOR LIVE
		return self.write(cr,uid,ids,{'state':'warehouse'})
		# return False
	def draft_force_assign(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'confirmed'})

	def setdraft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'draft'})

stock_picking()

class PurchaseOrder(osv.osv):
	_inherit = "purchase.order"
	# def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
 #        return {
 #            'name': order_line.name or '',
 #            'product_id': order_line.product_id.id,
 #            'product_qty': order_line.product_qty,
 #            'product_uos_qty': order_line.product_qty,
 #            'product_uom': order_line.product_uom.id,
 #            'product_uos': order_line.product_uom.id,
 #            'date': self.date_to_datetime(cr, uid, order.date_order, context),
 #            'date_expected': self.date_to_datetime(cr, uid, order_line.date_planned, context),
 #            'location_id': order.partner_id.property_stock_supplier.id,
 #            'location_dest_id': order.location_id.id,
 #            'picking_id': picking_id,
 #            'partner_id': order.dest_address_id.id or order.partner_id.id,
 #            'move_dest_id': order_line.move_dest_id.id,
 #            'state': 'draft',
 #            'type':'in',
 #            'purchase_line_id': order_line.id,
 #            'company_id': order.company_id.id,
 #            'price_unit': order_line.price_unit
 #        }
	def _create_pickings(self, cr, uid, order, order_lines, picking_id=False, context=None):
		"""Creates pickings and appropriate stock moves for given order lines, then
		confirms the moves, makes them available, and confirms the picking.

		If ``picking_id`` is provided, the stock moves will be added to it, otherwise
		a standard outgoing picking will be created to wrap the stock moves, as returned
		by :meth:`~._prepare_order_picking`.

		Modules that wish to customize the procurements or partition the stock moves over
		multiple stock pickings may override this method and call ``super()`` with
		different subsets of ``order_lines`` and/or preset ``picking_id`` values.

		:param browse_record order: purchase order to which the order lines belong
		:param list(browse_record) order_lines: purchase order line records for which picking
												and moves should be created.
		:param int picking_id: optional ID of a stock picking to which the created stock moves
							   will be added. A new picking will be created if omitted.
		:return: list of IDs of pickings used/created for the given order lines (usually just one)
		"""
		if not picking_id:
			picking_id = self.pool.get('stock.picking').create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
		todo_moves = []
		stock_move = self.pool.get('stock.move')
		wf_service = netsvc.LocalService("workflow")
		for order_line in order_lines:
			if not order_line.product_id:
				continue
			if order_line.product_id.type in ('product', 'consu'):
				if order_line.product_id.bom_ids:
					if order_line.product_id.bom_ids[0].bom_lines:
						for bom in order_line.product_id.bom_ids[0].bom_lines:
							moveBom = {
								'name': bom.product_id.name_template or order_line.name or '',
					            'product_id': bom.product_id.id,
					            'product_qty': order_line.product_qty,
					            'product_uos_qty': order_line.product_qty*bom.product_qty,
					            'product_uom': bom.product_uom.id,
					            'product_uos': bom.product_uom.id,
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
							move = stock_move.create(cr,uid,moveBom)
							todo_moves.append(move)

				else:
					move = stock_move.create(cr, uid, self._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context))
					if order_line.move_dest_id:
						order_line.move_dest_id.write({'location_id': order.location_id.id})
					todo_moves.append(move)
		stock_move.action_confirm(cr, uid, todo_moves)
		stock_move.force_assign(cr, uid, todo_moves)
		wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
		return [picking_id]
	



class move_set_data(osv.osv):
	_name = "move.set.data"
	_description = "Move Set Data"
	_rec_name = "origin_move_id"
	_columns = {

		'origin_move_id'    :   fields.integer('Origin Move ID',required=False), 
		'product_id'        :   fields.many2one('product.product',required=True,string="Product"),
		'product_qty'       :   fields.float('Quantity',required=True),
		'product_uom'       :   fields.many2one('product.uom',string="UOM"),
		'location_id'       :   fields.many2one('stock.location', 'Source Location'),
		'location_dest_id'  :   fields.many2one('stock.location', 'Destination Location'),
		'type'              :   fields.char('type'),
		'no'                :   fields.integer('No'),
		'desc'              :   fields.text('Description'),
		'picking_id'        :   fields.many2one('stock.picking',string="Picking",ondelete="cascade"),
	}
	

class stock_picking_out(osv.osv):

	_inherit = "stock.picking.out"
	_columns = {
		'note_id': fields.many2one('delivery.note','Delivery Note', select=True)
	}
	
stock_picking_out()


class sale_order_line(osv.osv):
	
	_inherit = 'sale.order.line'
	_columns = {
		'product_onhand': fields.float('On Hand', digits_compute= dp.get_precision('Product UoS'), readonly=True, states={'draft': [('readonly', False)]}),
		'product_future': fields.float('Available', digits_compute= dp.get_precision('Product UoS'), readonly=True, states={'draft': [('readonly', False)]}),
	}
	def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
		context = context or {}
		lang = lang or context.get('lang',False)
		if not  partner_id:
			raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
		warning = {}
		product_uom_obj = self.pool.get('product.uom')
		partner_obj = self.pool.get('res.partner')
		product_obj = self.pool.get('product.product')
		context = {'lang': lang, 'partner_id': partner_id}
		if partner_id:
			lang = partner_obj.browse(cr, uid, partner_id).lang
		context_partner = {'lang': lang, 'partner_id': partner_id}
		if not product:
			return {'value': {'th_weight': 0,
				'product_uos_qty': qty}, 'domain': {'product_uom': [],
				   'product_uos': []}}
		if not date_order:
			date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

		result = {}
		warning_msgs = ''
		product_obj = product_obj.browse(cr, uid, product, context=context_partner)
		result['product_uom'] = product_obj.uom_id.id

		uom2 = False
		if uom:
			uom2 = product_uom_obj.browse(cr, uid, uom)
			if product_obj.uom_id.category_id.id != uom2.category_id.id:
				uom = False
		if uos:
			if product_obj.uos_id:
				uos2 = product_uom_obj.browse(cr, uid, uos)
				if product_obj.uos_id.category_id.id != uos2.category_id.id:
					uos = False
			else:
				uos = False
		fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
		if update_tax: #The quantity only have changed
			result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

		tambah = ''
		if product_obj.description:
			tambah = '\n'+product_obj.description
		if not flag:
			result['name'] = '[' + product_obj.default_code + '] ' + product_obj.name_template+tambah #self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]+tambah
			if product_obj.description_sale:
				result['name'] += '\n'+product_obj.description_sale+tambah
		domain = {}
		if (not uom) and (not uos):
			result['product_uom'] = product_obj.uom_id.id
			if product_obj.uos_id:
				result['product_uos'] = product_obj.uos_id.id
				result['product_uos_qty'] = qty * product_obj.uos_coeff
				uos_category_id = product_obj.uos_id.category_id.id
			else:
				result['product_uos'] = False
				result['product_uos_qty'] = qty
				uos_category_id = False
			result['th_weight'] = qty * product_obj.weight
			domain = {'product_uom':
						[('category_id', '=', product_obj.uom_id.category_id.id)],
						'product_uos':
						[('category_id', '=', uos_category_id)]}
		elif uos and not uom: # only happens if uom is False
			result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
			result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
			result['th_weight'] = result['product_uom_qty'] * product_obj.weight
		elif uom: # whether uos is set or not
			default_uom = product_obj.uom_id and product_obj.uom_id.id
			q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
			if product_obj.uos_id:
				result['product_uos'] = product_obj.uos_id.id
				result['product_uos_qty'] = qty * product_obj.uos_coeff
			else:
				result['product_uos'] = False
				result['product_uos_qty'] = qty
			result['th_weight'] = q * product_obj.weight        # Round the quantity up

		if not uom2:
			uom2 = product_obj.uom_id
		# get unit price
		
		# if not pricelist:
		#     warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
		#             'Please set one before choosing a product.')
		#     warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
		# else:
		#     price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
		#             product, qty or 1.0, partner_id, {
		#                 'uom': uom or result.get('product_uom'),
		#                 'date': date_order,
		#                 })[pricelist]
		#     if price is False:
		#         warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
		#                 "You have to change either the product, the quantity or the pricelist.")

		#         warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
		#     else:
		#         result.update({'price_unit': price})
		# if warning_msgs:
		#     warning = {
		#                'title': _('Configuration Error!'),
		#                'message' : warning_msgs
		#             }

		# SCRIPT PROTECT STOCK AVAILABEL SALES ORDER LINE
		if product_obj.not_stock == False:
			if qty > product_obj.virtual_available:
				warning_msgs += _("Not enough stock Available")
				protect = {
						'title':_('Protect Stock Product !'),
						'message': warning_msgs
					}
				# return {'value':{'product_uom_qty':0,'product_uos_qty':0} , 'warning':protect}
		result['product_onhand'] = product_obj.qty_available
		result['product_future'] = product_obj.virtual_available
		
		
		return {'value': result, 'domain': domain, 'warning': warning}


class product_product(osv.osv):
	_inherit = "product.product"
	_columns = {
		'batch_code':fields.char('Batch No', size=64),
		'expired_date' : fields.date('Expired Date'),
		'partner_code':fields.char('Partner Code', size=64),
		'partner_desc' : fields.char('Partner Description', size=254),
	}
	
product_product()


class procurement_order(osv.osv):
	_inherit = "procurement.order"
	
	def action_confirm(self, cr, uid, ids, context=None):
		""" Confirms procurement and writes exception message if any.
		@return: True
		"""
		move_obj = self.pool.get('stock.move')
		for procurement in self.browse(cr, uid, ids, context=context):
			if procurement.product_qty <= 0.00:
				pass
				#raise osv.except_osv(_('Data Insufficient!'),
				#    _('Please check the quantity in procurement order(s) for the product "%s", it should not be 0 or less!' % procurement.product_id.name))
			if procurement.product_id.type in ('product', 'consu'):
				if not procurement.move_id:
					source = procurement.location_id.id
					if procurement.procure_method == 'make_to_order':
						source = procurement.product_id.property_stock_procurement.id
					id = move_obj.create(cr, uid, {
						'name': procurement.name,
						'location_id': source,
						'location_dest_id': procurement.location_id.id,
						'product_id': procurement.product_id.id,
						'product_qty': procurement.product_qty,
						'product_uom': procurement.product_uom.id,
						'date_expected': procurement.date_planned,
						'state': 'draft',
						'company_id': procurement.company_id.id,
						'auto_validate': True,
					})
					move_obj.action_confirm(cr, uid, [id], context=context)
					self.write(cr, uid, [procurement.id], {'move_id': id, 'close_move': 1})
		self.write(cr, uid, ids, {'state': 'confirmed', 'message': ''})
		return True

	
procurement_order()

class delivery_note(osv.osv):
	def print_dn_out(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"delivery-note/print&id="+str(ids[0])+"&uid="+str(uid)
		
		
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'print.int.move',
			'params': {
				# 'id'	: ids[0],
				'redir'	: urlTo,
				'uid':uid
			},
		}
	def print_pack_list(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		urlTo = str(browseConf.value)+"delivery-note/print-pack&id="+str(ids[0])+"&uid="+str(uid)
		
		
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'print.int.move',
			'params': {
				'redir'	: urlTo,
				'uid':uid
			},
		}
	_name = "delivery.note"

	_columns = {
		'name': fields.char('Delivery Note', required=True, size=64, readonly=True, states={'draft': [('readonly', False)]}),
		'prepare_id': fields.many2one('order.preparation', 'Order Packaging', domain=[('state', 'in', ['approve','done'])], required=False, readonly=True, states={'draft': [('readonly', False)]}),
		'tanggal' : fields.date('Delivery Date',track_visibility='onchange'),
		'state': fields.selection([('draft', 'Draft'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Cancel')], 'State', readonly=True,track_visibility='onchange'),
		'note_lines': fields.one2many('delivery.note.line', 'note_id', 'Note Lines', readonly=True, states={'draft': [('readonly', False)]}),
		'poc': fields.char('Customer Reference', size=64,track_visibility='onchange'),
		'partner_id': fields.many2one('res.partner', 'Customer', domain=[('customer','=', True)], readonly=True, states={'draft': [('readonly', False)]}),
		'partner_shipping_id': fields.many2one('res.partner', 'Delivery Address', domain=[('customer','=', True)], readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange'),
		'write_date': fields.datetime('Date Modified', readonly=True),
		'write_uid':  fields.many2one('res.users', 'Last Modification User', readonly=True),
		'create_date': fields.datetime('Date Created', readonly=True),
		'create_uid':  fields.many2one('res.users', 'Creator', readonly=True),
		'packing_lines': fields.one2many('packing.list.line', 'note_id', 'Packing List'),
		'note': fields.text('Notes'),
		'terms':fields.text('Terms & Condition'),
		'attn':fields.many2one('res.partner',string="Attention"),
	}
	_defaults = {
		'name': '/',
		'state': 'draft', 
	}
	# to add mail thread in footer
	_inherit = ['mail.thread']
	
	 
	_order = "name desc"


	def print_deliveryA4(self, cr, uid, ids, context=None):
		data = {}
		val = self.browse(cr, uid, ids)[0]
		data['form'] = {}
		data['ids'] = context.get('active_ids',[])
		data['form']['data'] = self.read(cr, uid, ids)[0]
		
		data['form']['data']['street'] = str(val.partner_shipping_id.street)
		data['form']['data']['jalan'] = str(val.partner_shipping_id.street2)
		data['form']['data']['phone'] = str(val.partner_shipping_id.phone)
		
		qty = ''
		product_name = ''
		product_code = ''
		for x in val.note_lines:
			qty = qty + str(x.product_qty) + ' ' + x.product_uom.name + '\n\n'
			product_name = product_name + x.name + '\n\n'
			product_code = product_code + x.product_id.code + '\n\n'
		
		data['form']['data']['qty'] = qty
		data['form']['data']['product_name'] = product_name
		data['form']['data']['product_code'] = product_code
			  
		return {
				'type': 'ir.actions.report.xml',
				'report_name': 'delivery.note.A4',
				'datas': data,
				'nodestroy':True
		}
	
	 
	def create(self, cr, uid, vals, context=None):
		# validate dn input
		print vals
		prepareExists = self.search(cr,uid,[('prepare_id','=',vals['prepare_id']),('state','not in',['cancel'])])
		print "-----------------------------",prepareExists
		if prepareExists:
			no = ""
			for nt in self.browse(cr,uid,prepareExists,context):
				no += "["+nt.name+"]\n"
			raise osv.except_osv(_("Error!!!"),_("Deliver Note ref to requested DO NO is Exist On NO "+no))


		if vals['special']==True:
			rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
			# saleid = self.pool.get('order.preparation').browse(cr, uid, vals['prepare_id']).sale_id.id
			usa = 'SPC'
			val = self.pool.get('ir.sequence').get(cr, uid, 'delivery.note').split('/')
			use = str(self.pool.get('res.users').browse(cr, uid, uid).initial)
			vals['name'] =time.strftime('%y')+ val[-1]+'C/SBM-ADM/'+usa+'-'+use+'/'+rom[int(val[2])]+'/'+val[1]
			return super(delivery_note, self).create(cr, uid, vals, context=context)
		else:    
			# ex: 000001C/SBM-ADM/JH-NR/X/13
			rom = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
			saleid = self.pool.get('order.preparation').browse(cr, uid, vals['prepare_id']).sale_id.id
			usa = str(self.pool.get('sale.order').browse(cr, uid, saleid).user_id.initial)
			val = self.pool.get('ir.sequence').get(cr, uid, 'delivery.note').split('/')
			use = str(self.pool.get('res.users').browse(cr, uid, uid).initial)
			vals['name'] =time.strftime('%y')+ val[-1]+'C/SBM-ADM/'+usa+'-'+use+'/'+rom[int(val[2])]+'/'+val[1]
			return super(delivery_note, self).create(cr, uid, vals, context=context)
	def package_draft(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'draft'})
		return True                               
	
	def package_cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'cancel'})
		return True                                  
		 
	def package_confirm(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		for x in val.note_lines:
			if x.product_qty <= 0:
				raise osv.except_osv(('Perhatian !'), ('Quantity product harus lebih besar dari 0 !'))
		self.write(cr, uid, ids, {'state': 'approve'})
		return True
		 
	def unlink(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		if val.state != 'draft':
			raise osv.except_osv(('Invalid action !'), ('Cannot delete a delivery note which is in state \'%s\'!') % (val.state,))
		return super(delivery_note, self).unlink(cr, uid, ids, context=context)
		  
	def prepare_change(self, cr, uid, ids, pre):
		if pre :
			res = {}; line = []
			data = self.pool.get('order.preparation').browse(cr, uid, pre)
			dnid = self.pool.get('delivery.note').search(cr, uid, [('prepare_id', '=', pre), ('state', '=', 'done')])
			for x in data.prepare_lines:
				qty = x.product_qty 
				if dnid:
					dnlid = self.pool.get('delivery.note.line').search(cr, uid, [('note_id', 'in', tuple(dnid)), ('product_id', '=', x.product_id.id)])
					if dnlid:
						dnldt = self.pool.get('delivery.note.line').browse(cr, uid, dnlid)
						qty -= sum([i.product_qty for i in dnldt])
				line.append({
							 'no': x.no,
							 'product_id' : x.product_id.id,
							 'product_qty': qty,
							 'product_uom': x.product_uom.id,
							 'name': x.name,
							 'op_line_id':x.id
							 })
			 
			res['note_lines'] = line
			res['poc'] = data.sale_id.client_order_ref
			res['tanggal'] = data.duedate
			res['partner_id'] = data.sale_id.partner_id.id
			res['partner_shipping_id'] = data.sale_id.partner_shipping_id.id
			res['attn'] = data.sale_id.attention.id
			
			return  {'value': res}
					 

	def package_validate(self, cr, uid, ids, context=None):

		val = self.browse(cr, uid, ids, context={})[0]
		print val.special

		print '==================================',val.prepare_id.picking_id.state
		if val.special==False:
			if val.prepare_id.picking_id.state == 'confirmed' or val.prepare_id.picking_id.state == 'assigned':
				if val.prepare_id is None:
					raise osv.except_osv(('Perhatian !'), ('Input Order Packaging Untuk Validate'))
				else:
					stock_move = self.pool.get('stock.move')
					stock_picking = self.pool.get("stock.picking")

					move = [x.product_id.id for x in val.prepare_id.picking_id.move_lines]
					print "PREPARE ======= ",val.prepare_id
					# return False
					line = [x.product_id.id for x in val.note_lines]
					err = [x for x in line if x not in move]
					if err:
						v = self.pool.get('product.product').browse(cr, uid, err)[0].default_code
						raise osv.except_osv(('Invalid action !'), ('Product \'%s\' tidak ada didalam daftar order !') % (v,))
					   
					for x in val.note_lines:
						if x.product_qty <= 0:
							raise osv.except_osv(('Perhatian !'), ('Quantity product harus lebih besar dari 0 !'))
						
						for z in val.prepare_id.picking_id.move_lines:
							#print '============================',z.sale_line_id.product_uom_qty
							if x.product_id.id == z.product_id.id:
								if x.product_qty > z.sale_line_id.product_uom_qty:
									y = self.pool.get('product.product').browse(cr, uid, x.product_id.id).default_code
							   # raise osv.except_osv(('Perhatian !'), ('Quantity product \'%s\' lebih besar dari quantity order !') % (y,))
						
					partial_data = {'min_date' : val.tanggal}
					for b in val.note_lines:
						move_id = False
						mid = stock_move.search(cr, uid, [('picking_id', '=', val.prepare_id.picking_id.id), ('product_id', '=', b.product_id.id)])[0]
						mad = stock_move.browse(cr, uid, mid)
						if b.product_qty == mad.product_qty:
							move_id = mid
						else:
							stock_move.write(cr,uid, [mid], {
								'product_qty': mad.product_qty-b.product_qty}
							)
							move_id = stock_move.create(cr,uid, {
											'name' : val.name,
											'product_id': b.product_id.id,
											'product_qty': b.product_qty,
											'product_uom': b.product_uom.id,
											'prodlot_id': mad.prodlot_id.id,
											'location_id' : mad.location_id.id,
											'location_dest_id' : mad.location_dest_id.id,
											'picking_id': val.prepare_id.picking_id.id})
							stock_move.action_confirm(cr, uid, [move_id], context)
							   
						partial_data['move%s' % (move_id)] = {
							'product_id': b.product_id.id,
							'product_qty': b.product_qty,
							'product_uom': b.product_uom.id,
							'prodlot_id': mad.prodlot_id.id}
						# self.pool.get().write(cr,uid,val.prepare_id,{'picking_id':})
					iddo = stock_picking.do_partial(cr, uid, [val.prepare_id.picking_id.id], partial_data)
					id_done = iddo.items()
					getMove = self.pool.get('stock.move').browse(cr,uid,move_id,context={})
					prepare_obj = self.pool.get('order.preparation')
					print "sacsacsacsacsac-----------------------",id_done[0]
					prepare_obj.write(cr,uid,[val.prepare_id.id],{'picking_id':getMove.picking_id.id})

					stock_picking.write(cr,uid, [id_done[0][1]['delivered_picking']], {'note_id': val.id})

					self.write(cr, uid, ids, {'state': 'done', 'picking_id': id_done[0][1]['delivered_picking']})

					# print "AAAAAAAAAAAAAAAAAAAAa=====",st
					# print "BBBBBBBBBBBBBBBB",st.id
					# print "BBBBBBBBBBBBBBBB",stock_picking.id
					# print "ID DO ===========================",iddo
					# print "ID DONEEEEEEE =+++=============",id_done

					print "MOVE ID SSSS",move_id
					print partial_data,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
					print val.prepare_id,">>>>>>>><<<>>>>>>>>>>>>>>>>>>>>>>>>..================"
					
					# print "GET MOVE === ",getMove.picking_id
					# return False
					# self.pool.get('order.preparation').write(cr,uid,val.prepare_id,{'picking_id':getMove.picking_id.id})

					return True
			else:
				self.write(cr, uid, ids, {'state': 'done'})
				return True
		else:
			self.write(cr, uid, ids, {'state': 'done'})
			return True
			
		return False
delivery_note()
 

class delivery_note_line(osv.osv):
	_name = "delivery.note.line"
	_columns = {
		'no': fields.integer('No'),
		'name': fields.text('Description'),
		'note_id': fields.many2one('delivery.note', 'Delivery Note', required=True, ondelete='cascade'),
		'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)]),
		'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
		'product_uom': fields.many2one('product.uom', 'UoM'),
		'product_packaging': fields.many2one('product.packaging', 'Packaging'),
		'op_line_id':fields.many2one('order.preparation.line','OP Line',required=True),

	}
		 
delivery_note_line()


class packing_list_line(osv.osv):
	_name = "packing.list.line"
	_columns = {
		'name': fields.char('Package', size=64),
		'color': fields.char('Color Code', size=64),
		'urgent':fields.char('Urgent',size=64),
		'product_lines': fields.one2many('product.list.line', 'packing_id', 'Packing List'),
		'note_id': fields.many2one('delivery.note', 'Delivery Note', required=True, ondelete='cascade'),
	}
	

	def refresh(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]
		for x in val.note_id.note_lines:
			self.pool.get('product.list.line').create(cr, uid, {
														  'no': x.no,
														  'name': x.name,
														  'packing_id': val.id,
														  'product_id': x.product_id.id,
														  'product_qty': x.product_qty,
														  'product_uom': x.product_uom.id,
														  'product_packaging': x.product_packaging.id,
														  })
		return True

		 
	def print_packaging(self, cr, uid, ids, context=None):
		data = {}
		val = self.browse(cr, uid, ids)[0]
		data['form'] = {}
		data['ids'] = context.get('active_ids',[])
		data['form']['data'] = self.read(cr, uid, ids)[0]
		
		no = ''; qty = ''; product = ''; weight = ''; measurement = ''
		for x in val.product_lines:
			
			no = no + str(x.no) + '\n\n'
			measurement = measurement + str(x.measurement) + '\n\n'
			weight = weight + str(x.weight) + '\n\n'
			qty = qty + str(x.product_qty) + ' ' + x.product_uom.name + '\n\n'
			product = product + x.name + '\n\n'
			 
		data['form']['data']['no'] = no
		data['form']['data']['qty'] = qty
		data['form']['data']['weight'] = weight
		data['form']['data']['product'] = product
		data['form']['data']['measurement'] = measurement
		
		data['form']['data']['name'] = val.note_id.partner_id.name
		data['form']['data']['attention'] = val.note_id.prepare_id.sale_id.attention.name
		data['form']['data']['date'] = val.note_id.create_date
		data['form']['data']['reference'] = val.note_id.name
		
		data['form']['data']['purchase'] = val.note_id.poc
		data['form']['data']['pur_date'] = val.note_id.prepare_id.sale_id.date_order
		
		
		 
		return {
				'type': 'ir.actions.report.xml',
				'report_name': 'paket.A4',
				'datas': data,
				'nodestroy':True
		}


packing_list_line()   

class product_list_line(osv.osv):
	_name = "product.list.line"
	_columns = {
		'no': fields.integer('No', size=3),
		'weight': fields.char('weight', size=128),
		'measurement': fields.char('measurement', size=128),
		'name': fields.text('Description'),
		'packing_id': fields.many2one('packing.list.line', 'Packing List', required=True, ondelete='cascade'),
		'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)]),
		'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
		'product_uom': fields.many2one('product.uom', 'UoM'),
	}
		 
product_list_line()   


class stock_move(osv.osv):
	_inherit = "stock.move"
	_columns = {
		'no': fields.integer('No', size=3),
		'desc':fields.text('Description',required=False),
		'name':fields.text('Product Name',required=False),
		'set_id':fields.many2one('move.set.data',string="Set Product",ondelete="cascade")
	}
	
	# def onchange_product_id(self,cr,uid,ids,prd,location_id, location_dest_id, partner):
	#     hasil=self.pool.get('product.product').browse(cr,uid,[prd])[0]
	#     uom=self.pool.get('product.template').browse(cr,uid,[prd])[0]
	#     return {'value':{ 'desc':hasil.name, 'product_qty':1, 'product_uom':uom.uom_id.id} }
	def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
							loc_dest_id=False, partner_id=False):
		""" On change of product id, if finds UoM, UoS, quantity and UoS quantity.
		@param prod_id: Changed Product id
		@param loc_id: Source location id
		@param loc_dest_id: Destination location id
		@param partner_id: Address id of partner
		@return: Dictionary of values
		"""
		if not prod_id:
			return {}
		user = self.pool.get('res.users').browse(cr, uid, uid)
		lang = user and user.lang or False
		if partner_id:
			addr_rec = self.pool.get('res.partner').browse(cr, uid, partner_id)
			if addr_rec:
				lang = addr_rec and addr_rec.lang or False
		ctx = {'lang': lang}

		product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]
		uos_id  = product.uos_id and product.uos_id.id or False
		result = {
			'product_uom': product.uom_id.id,
			'product_uos': uos_id,
			'product_qty': 1.00,
			'product_uos_qty' : self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty'],
			'prodlot_id' : False
		}
		if product.description:
			result['desc'] = product.name + '\n\n' + product.description
		else:
			result['desc'] = product.name

		if not ids:
			result['name'] = product.partner_ref
		if loc_id:
			result['location_id'] = loc_id
		if loc_dest_id:
			result['location_dest_id'] = loc_dest_id
		return {'value': result}
   
stock_move()
