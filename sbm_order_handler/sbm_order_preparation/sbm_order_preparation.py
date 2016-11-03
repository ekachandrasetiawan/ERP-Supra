import time
import netsvc
import openerp.exceptions
import decimal_precision as dp
import re
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from openerp.addons.mail.tests.test_mail_base import TestMailBase
import logging

_logger = logging.getLogger(__name__)


class order_preparation(osv.osv):
	_inherit = "order.preparation"
	_description = "Order Packaging"
	_columns = {
		'poc': fields.char('Customer Reference', size=64,track_visibility='onchange',readonly=True, states={'draft': [('readonly', False)]}),
		'name': fields.char('Reference', required=True, size=64, select=True, readonly=True, states={'draft': [('readonly', False)]}),
		'sale_id': fields.many2one('sale.order', 'Sale Order', select=True, required=False, readonly=True, domain=['|', ('quotation_state','=','win'),('state','in',['progress','manual'])], states={'draft': [('readonly', False)]}),
		'picking_id': fields.many2one('stock.picking', 'Delivery Order', required=False, domain="[('sale_id','=', sale_id), ('state','not in', ('cancel','done'))]", readonly=True, states={'draft': [('readonly', False)]},track_visibility='always'),
		'duedate' : fields.date('Delivery Date', readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange'),
		'location_id':fields.many2one('stock.location',required=False,string='Picking Location',readonly=True, states={'draft': [('readonly', False)]}),
		'state': fields.selection([('draft', 'Draft'), ('submited','Submited'), ('approve', 'Approved'), ('cancel', 'Cancel'), ('done', 'Done')], 'State', readonly=True, track_visibility='onchange'),
		'warehouse_notes':fields.text('Warehouse Notes', readonly=True),
		'sbm_wo_id':fields.many2one('sbm.work.order', 'W.O/SPK', track_visibility="onchange", readonly=True, states={'draft': [('readonly', False)]}),
		'is_postpone':fields.boolean(string='Is Postpone', track_visibility='onchange',readonly=True, states={'draft': [('readonly', False)]}),
	}

	_track = {
		'state':{
			'order_preparation.op_pack_submited': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'submited',
			'order_preparation.op_pack_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approved',
			'order_preparation.op_pack_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
			'order_preparation.op_pack_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
		},
	}

	_order = "id desc"

	def picking_change(self,cr,uid,ids,picking_id,context={}):
		res = False
		if picking_id:
			pick = self.pool.get('stock.picking').browse(cr,uid,picking_id)
			is_so_has_material = False
			# check if so already has material
			for ol in pick.sale_id.order_line:
				for material in ol.material_lines:
					is_so_has_material = True
			# if so has material
			# if is_so_has_material:
			# 	# maybe its old so  but already partialed order
			# 	# means maybe in past some item has been delivered
			# 	# need check is moves has material line id
			# 	is_move_linked_to_material = False
			# 	for move in pick.move_lines:
			# 		if move.sale_material_id:
			# 			is_move_linked_to_material  = True
			# 	if not is_move_linked_to_material:
			# 		# if not linked it means so is old so,, so confirmed has picking
			# 		# then we need to rewrite sale order material line into stock move

			# 		self.pool.get('sale.order').generate_material(cr,uid,move.sale_line_id.order_id.id,context=None)
			# 		# then we need to re call sale_change_id after material generated
			# 		return self.sale_change(cr, uid, ids, move.sale_line_id.order_id.id, False, context=context)

			# 	else:
			# 		# if stock move has sale_material_id then it means its picking is partial on old so processing
			# 		# then we just only need to load line
			# 		print "aAAA"

			# else:
			# 	# if so does not has material
			# 	# it means old so,, and not delivered yet
			# 	print "BBBB"
			res = super(order_preparation,self).picking_change(cr,uid,ids,picking_id)
			if pick:
				res['value']['partner_id'] = pick.sale_id.partner_id.id
				res['value']['partner_shipping_id'] = pick.sale_id.partner_shipping_id.id
				res['value']['poc'] = pick.sale_id.client_order_ref
				print res,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
				# for prepare_line in res['value']['prepare_lines']

		return res
		

	def _set_message_unread(self, cr, uid, ids, context=None):
		m  = self.pool.get('ir.model.data')
		id_group = m.get_object(cr, uid, 'sbm_order_handler', 'group_admin_ho').id
		user_group = self.pool.get('res.groups').browse(cr, uid, id_group)
		for x in user_group.users:
			if x.id:
				cr.execute('''
					UPDATE mail_notification SET
						read=false
					WHERE
						message_id IN (SELECT id from mail_message where res_id=any(%s) and model=%s) and
						partner_id = %s
				''', (ids, 'order.preparation', x.partner_id.id))
		return True

	def _set_mail_notification(self, cr, uid, ids, partner_id, context=None):
		message = self.pool.get('mail.message')

		mail_message = message.search(cr, uid, [('res_id', '=',ids),('model', '=', 'order.preparation')])
		mail_id = message.browse(cr, uid, mail_message)

		for x in mail_id:
			if x.parent_id.id == False:
				id_notif = self.pool.get('mail.notification').create(cr, uid, {
							'read': False,
							'message_id': x.id,
							'partner_id': partner_id,
						}, context=context)

			# Delete Message Post Message
			if x.body=='<p>Post Message</p>':
				message.unlink(cr,uid,[x.id],context)

		return True

	def _set_op_followers(self, cr, uid, ids, context=None):
		m  = self.pool.get('ir.model.data')
		id_group = m.get_object(cr, uid, 'sbm_order_handler', 'group_admin_ho').id
		user_group = self.pool.get('res.groups').browse(cr, uid, id_group)

		# Create Mail Post
		msg = _("Post Message")
		self.message_post(cr, uid, [ids], body=msg, context=context)

		for x in user_group.users:
			# Create By Mail Followers
			if x.id <> uid:
				if x.partner_id.id:
					id_mail = self.message_subscribe(cr, uid, [ids], [x.partner_id.id], subtype_ids=None, context=context)

			# Create By Mail Notification
			if x.partner_id.id:
				self._set_mail_notification(cr, uid, ids, x.partner_id.id, context=None)


		return True

	def send_email(self, cr, uid, ids, subject, context=None):
		val = self.browse(cr, uid, ids)[0]
		mail_mail = self.pool.get('mail.mail')
		obj_usr = self.pool.get('res.users')
		obj_partner = self.pool.get('res.partner')

		username = obj_usr.browse(cr, uid, uid)
		

		ip_address = '192.168.9.26:10001'
		db = 'LIVE_2014'
		url = 'http://'+ip_address+'/?db='+db+'#id=' +str(val.id)+'&view_type=form&model=order.preparation&menu_id=529&action=498'

		# Group warehouse User
		p  = self.pool.get('ir.model.data')
		warehouse_user = p.get_object(cr, uid, 'stock', 'group_stock_user').id
		user_warehouse = self.pool.get('res.groups').browse(cr, uid, warehouse_user)

		for x in ids:
			if val.state == 'submited':
				for user in user_warehouse.users:
					body = """\
						<html>
						  <head></head>
						  <body>
						    <p>
						    	Dear %s!<br/><br/>
								%s Telah Mensubmit Order Preparation <b> %s </b><br/>
								<br/>
								Silahkan klik Link ini untuk melihat detail Order Preparation. <a href="%s">View Order Preparation</a>
						    </p>
						    <br/>
						    Best Regards,<br/>
							Administrator ERP
						  </body>
						</html>
						""" % (user.name, username.name, val.name, url)

					mail_id = mail_mail.create(cr, uid, {
						'model': 'order.preparation',
						'res_id': x,
						'subject': subject,
						'body_html': body,
						'auto_delete': True,
						}, context=context)

					mail_mail.send(cr, uid, [mail_id], recipient_ids=[user.partner_id.id], context=context)
			else:
				cr.execute("SELECT create_uid FROM order_preparation WHERE id = %s", ids)
				id_user_create = map(lambda id: id[0], cr.fetchall())
				
				usr = obj_usr.browse(cr, uid, id_user_create)[0]
				body = """\
					<html>
					  <head></head>
					  <body>
					    <p>
					    	Dear %s!<br/><br/>
							%s Telah Memproses Order Preparation <b> %s </b> dan siap untuk dibuatkan surat jalan / Delivery Notes <br/>
							<br/>
							Silahkan klik Link ini untuk melihat detail Order Preparation.  <a href="%s">View Order Preparation</a>
					    </p>
					    <br/>
					    Best Regards,<br/>
						Administrator ERP
					  </body>
					</html>
					""" % (usr.name, username.name, val.name, url)

				mail_id = mail_mail.create(cr, uid, {
					'model': 'order.preparation',
					'res_id': x,
					'subject': subject,
					'body_html': body,
					'auto_delete': True,
					}, context=context)

				mail_mail.send(cr, uid, [mail_id], recipient_ids=[usr.partner_id.id], context=context)

		return True

	def validasi_create(self, cr, uid, vals, context=None):
		if 'prepare_lines' in vals:
			for x in vals['prepare_lines']:
				if x[2]:
					qty_note_line =  x[2]['product_qty']

					if x[2]['prodlot_id']:
						qty_bacth = 0
						for y in x[2]['prodlot_id']:
							qty_bacth += y[2]['qty']

						if qty_bacth < qty_note_line:
							raise osv.except_osv(('Warning..!!'), ('Please Check Qty Product Bacth'))
		return True

	def create(self, cr, uid, vals, context=None):
		self.validasi_create(cr, uid, vals, context=None)

		res = super(order_preparation, self).create(cr, uid, vals, context=context)
		self._set_op_followers(cr, uid, res, context=None)
		return res

	"""Action submit
	"""
	def preparation_submit(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]

		if val.picking_id.id:
			if val.picking_id.state == 'cancel':
				raise osv.except_osv(('Warning'), ('Delivery Order Status Cancel, Please Refresh Delivery Order '))

		res = False
		if self.validasi(cr, uid, ids, context=context):
			res = self.write(cr, uid, ids, {'state':'submited'}, context=context)
			subject = 'Order Preparation no' + val.name + ' Submited'

			self.send_email(cr, uid, ids, subject, context=None)
		return res

	def preparation_done(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]
		op_line_obj = self.pool.get('order.preparation.line')
		dn_obj = self.pool.get('delivery.note')
		dn_line_obj = self.pool.get('delivery.note.line')
		op_line_obj = self.pool.get('order.preparation.line')
		op_line_material_obj = self.pool.get('delivery.note.line.material')

		# Send Email
		subject = 'Order Preparation no' + val.name + ' Validate'
		self.send_email(cr, uid, ids, subject, context=None)

		self._set_message_unread(cr, uid, ids, context=None)
		res = super(order_preparation, self).preparation_done(cr, uid, ids, context=context)

		dn_exist = dn_obj.search(cr, uid, [('prepare_id','=',[val.id])],context=None)

		

		if not dn_exist and val.is_postpone == True:
			id_dn = self.create_delivery_note(cr, uid, ids, context=None)
			dn_obj.submit(cr, uid, id_dn, context=None)
			dn_obj.package_postpone(cr, uid, id_dn, context=None)
		elif dn_exist and val.is_postpone == False:
			prep_dn = {}
			evt_prepare_change = dn_obj.prepare_change(cr, uid, ids, val.id, validasi=True)
			prep_dn = evt_prepare_change['value']

			data_dn = dn_obj.browse(cr, uid, dn_exist, context=None)[0]

			for x in data_dn.note_lines:
				dn_line_obj.unlink(cr,uid,[x.id])
				
			dn_obj.write(cr,uid,dn_exist,prep_dn)

		return res

	def create_delivery_note(self, cr, uid, ids, context=None):
		res = False
		ops = self.browse(cr, uid, ids, context=context)
		dn_obj = self.pool.get('delivery.note')
		
		new_dn_ids = []
		for op in ops:
			prep_dn = {}
			evt_prepare_change = dn_obj.prepare_change(cr, uid, ids, op.id, validasi=False)
			prep_dn = evt_prepare_change['value']
			prep_dn['prepare_id']=op.id
			prep_dn['special']=False

			new_dn_ids.append(dn_obj.create(cr, uid, prep_dn, context=context))

		return new_dn_ids

	def set_delivery_notes(self, cr, uid, ids, context=None):

		new_dn_ids = self.create_delivery_note(cr, uid, ids, context=None)

		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ad_delivery_note', 'view_delivery_note_form')

		context.update({
			'active_model': self._name,
			'active_ids': new_dn_ids,
			'active_id': len(new_dn_ids) and new_dn_ids[0] or False
		})

		res = {
			'name': _('Delivery Note'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': [view_id],
			'res_model': 'delivery.note',
			'context': context,
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': new_dn_ids and new_dn_ids[0] or False,
		}

		return res

	def sbm_wo_change(self, cr, uid, ids, wo_id, context=None):
		work_order = self.pool.get('sbm.work.order')
		work_order_output = self.pool.get('sbm.work.order.output')
		work_order_material = self.pool.get('sbm.work.order.output.raw.material')
		res = {}; line = []
		if wo_id:
			wo = work_order.browse(cr, uid, [wo_id])[0]
			if wo.sale_order_id.id:
				wo_line = work_order_output.search(cr, uid, [('work_order_id', '=', wo_id)])
				no_line = 1
				for x in work_order_output.browse(cr, uid, wo_line, context=None):
					line.append((0,0,{
							'no': no_line,
							'product_id' : x.item_id.id,
							'name': x.desc,
							'detail': x.desc,
							'product_qty': x.qty,
							'product_uom': x.uom_id.id,
							'sale_line_material_id':x.sale_order_material_line.id
						}))
					no_line +=1
				res['location_id'] = wo.location_id.id
				res['sale_id'] = wo.sale_order_id.id
				res['poc'] = wo.sale_order_id.client_order_ref
				res['partner_shipping_id'] = wo.sale_order_id.partner_shipping_id.id
				res['duedate'] = wo.due_date
				res['partner_id'] = wo.customer_id.id
				res['prepare_lines'] = line
			else:
				raise osv.except_osv(_('Perhatian!'), _('Sales Order Not Found'))
		return {'value': res}

	def sale_change(self, cr, uid, ids, sale, loc=False, context=None):
		# default 
		res = {}
		res['picking_id'] = False
		so_material_line = self.pool.get('sale.order.material.line')
		obj_op_line = self.pool.get('order.preparation.line')
		obj_op = self.pool.get('order.preparation')
		obj_dn_line_mat = self.pool.get('delivery.note.line.material')
		obj_dn_line_mat_ret = self.pool.get('delivery.note.line.material.return')
		obj_move = self.pool.get('stock.move')

		so = self.pool.get('sale.order')
		_logger.error(('Tesss1---------------------',sale))
		if sale:
			_logger.error(('MASUKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK'))
			
			has_old_picking = False
			has_postpone_picking=False
			line = []
			data = self.pool.get('sale.order').browse(cr, uid, sale)

			# check if picking exist on Sale.Order object

		# if data.picking_ids:
			has_old_picking=True
			# if picking ids then we need to check state
			active = [] #list of browse record
			sale_material_id_generated = False
			for picking in data.picking_ids:
				if picking.state != 'cancel' and picking.state !='done':
					for move_line in picking.move_lines:
						if move_line.sale_material_id:
							sale_material_id_generated =True

					active.append(picking)
			if len(active)==1 and sale_material_id_generated == False:
				so.generate_material(cr,uid,sale,context=context)
				has_postpone_picking=True
				self.pool.get('stock.picking').action_cancel(cr, uid, [active[0].id])
				# res['picking_id'] = active[0].id
				# return {'value':res}

			res['poc'] = data.client_order_ref
			res['partner_id'] = data.partner_id.id
			res['duedate'] = data.delivery_date
			res['partner_shipping_id'] = data.partner_shipping_id.id

			location = []
			old_so_doc_ids = []
			for x in data.order_line:
				_logger.error(('LOop Order Line ++++++++++++++++++++++++', x))
				if x.material_lines == []:
					_logger.error(('MASUKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK IFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF x material lines'))
					# raise openerp.exceptions.Warning("SO Material Belum di Definisikan")
					old_so_doc_ids.append(x.order_id.id)

			for old_id in old_so_doc_ids:
				_logger.error(('GNERATING MATERIAL--------------------<<<<<<<<<<<<<<<<<<<'))
				so.generate_material(cr,uid,old_id,context=context)
				so.log(cr,uid,old_id,_('Automatic Generate Material by OP Sale Change!'))
			for x in data.order_line:
				# if loc:
				# 	material_lines=so_material_line.search(cr,uid,[('sale_order_line_id', '=' ,x.id), ('picking_location', '=' , loc)])
				# else:
				# 	material_lines=so_material_line.search(cr,uid,[('sale_order_line_id', '=' ,x.id)])

				material_lines=so_material_line.search(cr,uid,[('sale_order_line_id', '=' ,x.id)])


				theNum=1
				for y in so_material_line.browse(cr, uid, material_lines):
					# Cek Material Line Dengan OP Line
					nilai= 0 #nilai yang sudah di ambil item nya ke dalam op.
					op_line = []
					curr_op_id=ids

					op_line = obj_op_line.search(cr,uid,[('sale_line_material_id', '=' ,y.id),('preparation_id','not in',curr_op_id)])
					for l in obj_op_line.browse(cr, uid, op_line):
						# Cek Status OP 
						op=obj_op.browse(cr, uid, [l.preparation_id.id])[0]
						product_return = 0
						search_dn_lm=obj_dn_line_mat.search(cr, uid, [('op_line_id', 'in' , [l.id])])
						if len(search_dn_lm):
							search_cek_return=obj_dn_line_mat_ret.search(cr, uid, [('delivery_note_line_material_id', 'in' , [search_dn_lm])])
							# Cek DN Line Material Return
							for rn in obj_dn_line_mat_ret.browse(cr, uid, search_cek_return):
								if rn.stock_move_id.state == 'done':
									product_return += rn.stock_move_id.product_qty

						if op.state <> 'cancel':
							nilai += l.product_qty - product_return

					if y.product_id.type <> 'service':
						nilai = y.qty-y.shipped_qty-y.on_process_qty+y.returned_qty

						_logger.error(('bukan serviceEEEEEEEEEEEEEE--------------------<<<<<<<<<<<<<<<<<<<'))
						_logger.error(('Material QTY-------------',y.qty,y.shipped_qty,y.on_process_qty,y.returned_qty))
						_logger.error(('Nilai Nilai-------------',nilai))
						_logger.error(('Nilai QTY-------------',y.qty))
						if nilai:
							_logger.error(('Nilai <<<<<< QTYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'))

							location += [y.picking_location.id]
							if y.sale_order_line_id.product_no_cus:
								seq_no = int(y.sale_order_line_id.product_no_cus)
							elif y.sale_order_line_id.sequence:
								seq_no = y.sale_order_line_id.sequence
							else:
								seq_no = theNum


							line.append({
								'no': seq_no,
								'product_id' : y.product_id.id,
								# 'product_qty': y.qty - nilai,
								'product_qty': (y.qty + y.returned_qty) - (y.on_process_qty + y.shipped_qty), #nilai yang material line minta - op yang sudah di proses
								'product_uom': y.uom.id,
								'name': y.desc,
								'sale_line_material_id':y.id,
								'sale_line_id':y.sale_order_line_id.id
							})
							theNum=theNum+1 #append nomor urut
			res['prepare_lines'] = line
			_logger.error(('------------------------------------------------------Tesss2---------------------',res))
			return  {'value': res}


	def preparation_confirm(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]

		obj_op_line = self.pool.get('order.preparation.line')
		obj_op = self.pool.get('order.preparation')
		obj_dn_line_mat = self.pool.get('delivery.note.line.material')
		obj_dn_line_mat_ret = self.pool.get('delivery.note.line.material.return')
		obj_move = self.pool.get('stock.move')

		for x in val.prepare_lines:
			nilai= 0
			op_line = [] #assign default to 0 result
			if x.sale_line_material_id: #if not old order_preparation_data
				op_line=obj_op_line.search(cr,uid,[('sale_line_material_id', '=' ,x.sale_line_material_id.id)])

			for l in obj_op_line.browse(cr, uid, op_line):
				op=obj_op.browse(cr, uid, [l.preparation_id.id])[0]

				product_return = 0
				search_dn_lm=obj_dn_line_mat.search(cr, uid, [('op_line_id', 'in' , [l.id])])
				print "-----",l.id
				if search_dn_lm:
					search_cek_return=obj_dn_line_mat_ret.search(cr, uid, [('delivery_note_line_material_id', 'in' , search_dn_lm)])
					print 'AAAAAAAAAAAA ',search_cek_return
					# Cek DN Line Material Return
					for rn in obj_dn_line_mat_ret.browse(cr, uid, search_cek_return):
						if rn.stock_move_id.state == 'done':
							product_return += rn.stock_move_id.product_qty

				if op.state <> 'cancel':
					nilai += l.product_qty - product_return

			if x.sale_line_material_id.id:

				so_material_line=self.pool.get('sale.order.material.line').browse(cr, uid, [x.sale_line_material_id.id])[0]
				mm = ' ' + so_material_line.product_id.default_code + ' '
				msg = 'Product' + mm + 'Melebihi Order.!\n'

				if nilai > so_material_line.qty:
					raise openerp.exceptions.Warning(msg)

		self._set_message_unread(cr, uid, ids, context=None)
		validasi = self.validasi(cr, uid, ids, context=None)

		if validasi == True:
			self.write(cr, uid, ids, {'state': 'approve'})
			
		return False

	def validasi(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]
		notActiveProducts = []
		for x in val.prepare_lines:
			if not context:
				context = {}
			context['location'] = val.location_id.id
			product =self.pool.get('product.product').browse(cr, uid, x.product_id.id, context=context)
			if not product.active:
				if not re.match(r'service',product.categ_id.name,re.M|re.I) and not re.match(r'on it maintenance service',product.categ_id.name,re.M|re.I):
					notActiveProducts.append(product.default_code)	

			if product.not_stock == False:
				mm = ' ' + product.default_code + ' '
				stock = ' ' + str(product.qty_available) + ' '
				msg = 'Stock Product' + mm + 'Tidak Mencukupi.!\n'+ ' On Hand Qty '+ stock 

				if x.product_qty > product.qty_available:
					raise openerp.exceptions.Warning(msg)
					return False

				if product.track_outgoing:
					for batch in x.prodlot_id:
						prodlot_browse = self.pool.get('stock.production.lot').browse(cr, uid, batch.name.id, context=context)
						stock_batch = prodlot_browse.stock_available
						# _logger.error(('Tesss---------------------',batch.qty,'--',stock_batch, context, prodlot_browse))
						if batch.qty > stock_batch:
							stock = ' ' + str(stock_batch) + ' '
							msg = 'Stock Product' + mm + ' '+batch.name.name+' Tidak Mencukupi.!\n'+ ' On Hand Qty '+ stock 
							raise openerp.exceptions.Warning(msg)
							return False
					
		if len(notActiveProducts) > 0:
			m_p_error = ""
			for pNon in notActiveProducts:
				m_p_error+=pNon+",\r\n"
			m_p_error+="\r\n is non active product, please activate product first."

			raise osv.except_osv(_('Error!'),_(m_p_error))
		return True
		
	def preparation_draft(self, cr, uid, ids, context=None):

		self._set_message_unread(cr, uid, ids, context=None)
		return super(order_preparation, self).preparation_draft(cr, uid, ids, context=context)

	def preparation_cancel(self, cr, uid, ids, context=None):
		self._set_message_unread(cr, uid, ids, context=None)
		return super(order_preparation, self).preparation_cancel(cr, uid, ids, context=context)


	def action_wizard_order_preparation(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		op=self.pool.get('order.preparation')

		if context is None:
			context = {}
		
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_order_handler', 'wizard_order_preparation_form')

		context.update({
			'active_model': self._name,
			'active_ids': ids,
			'active_id': len(ids) and ids[0] or False
		})
		return {
			'view_mode': 'form',
			'view_id': view_id,
			'view_type': 'form',
			'view_name':'wizard_order_preparation_form',
			'res_model': 'wizard.order.preparation',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
			'nodestroy': True,
		}

order_preparation()

class order_preparation_line(osv.osv):
	_inherit = "order.preparation.line"
	_columns = {
		# 'cust_ref_no': fields.char('Cust Ref No', required=False),
		'product_id': fields.many2one('product.product', 'Product',track_visibility='always'),
		'product_uom': fields.many2one('product.uom', 'UoM'),
		'sale_line_id': fields.many2one('sale.order.line', "Sale Item", required=True),
		'sale_line_material_id': fields.many2one('sale.order.material.line', 'Material Ref', required=True),
	}

	def change_item(self, cr, uid, ids, item, context={}):
		product = self.pool.get('product.product').browse(cr, uid, item, context=None)
		return {'value':{'product_uom':product.uom_id.id}}

	def check_item_material(self, cr, uid, ids, item, context={}):

		return {'value':{'sale_line_material_id':False}}

order_preparation_line()

class WizardOrderPreparation(osv.osv_memory):

	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		op_ids = context.get('active_ids', [])
		active_model = context.get('active_model')
		res = super(WizardOrderPreparation, self).default_get(cr, uid, fields, context=context)
		if not op_ids or len(op_ids) != 1:
			return res
		op_id, = op_ids
		if op_id:
			res.update(op_id=op_id)
			po = self.pool.get('order.preparation').browse(cr, uid, op_id, context=context)		
		return res

	def request_op_validate(self,cr,uid,ids,context=None):
		data = self.browse(cr,uid,ids,context)[0]
		obj_op = self.pool.get('order.preparation')
		op_id = data.op_id.id
		# Validasi
		obj_op.preparation_done(cr, uid, [op_id])
		# Update Warehouse Notes
		obj_op.write(cr,uid,op_id,{'warehouse_notes':data.notes})

		return True

	_name="wizard.order.preparation"
	_description="Wizard Order Preparation"
	_columns = {
		'op_id':fields.many2one('order.preparation',string="Order Preparation"),
		'notes':fields.text('Notes',required=True, help="Warehouse Notes"),
	}

	_rec_name="op_id"

WizardOrderPreparation()


class sale_order_line(osv.osv):

	_inherit = 'sale.order.line'

	_columns = {
		'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True, required=True),
		'product_ref': fields.related('product_id','name',string='Product',readonly=True,type='char', help = 'The product part number'),
	}
	_rec_name = 'product_ref'

sale_order_line()


class sale_order_material_line(osv.osv):
	_inherit = 'sale.order.material.line'
	_description = 'Sale order material line'

	_columns = {
		'product_id':fields.many2one('product.product',string="Product", required=True, domain=[('sale_ok','=','True'),('categ_id.name','!=','LOCAL')], active=True),
		'product_ref': fields.related('product_id','name',string='Product',readonly=True,type='char', help = 'The product part number'),
	}

	_rec_name = 'product_ref'
	
sale_order_material_line()	