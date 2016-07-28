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

class order_preparation(osv.osv):
	_inherit = "order.preparation"
	_description = "Order Packaging"
	_columns = {
		'poc': fields.char('Customer Reference', size=64,track_visibility='onchange',readonly=True, states={'draft': [('readonly', False)]}),
		'name': fields.char('Reference', required=True, size=64, select=True, readonly=True, states={'draft': [('readonly', False)]}),
		'sale_id': fields.many2one('sale.order', 'Sale Order', select=True, required=True, readonly=True, domain=['|', ('quotation_state','=','win'),('state','in',['progress','manual'])], states={'draft': [('readonly', False)]}),
		'picking_id': fields.many2one('stock.picking', 'Delivery Order', required=False, domain="[('sale_id','=', sale_id), ('state','not in', ('cancel','done'))]", readonly=True, states={'draft': [('readonly', False)]},track_visibility='always'),
		'duedate' : fields.date('Delivery Date', readonly=True, states={'draft': [('readonly', False)]},track_visibility='onchange'),
		'location_id':fields.many2one('stock.location',required=True,string='Picking Location',readonly=True, states={'draft': [('readonly', False)]}),
		'state': fields.selection([('draft', 'Draft'), ('submited','Submited'), ('approve', 'Approved'), ('cancel', 'Cancel'), ('done', 'Done')], 'State', readonly=True, track_visibility='onchange'),

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

	def picking_change(self,cr,uid,ids,picking_id):
		res = False
		if picking_id:
			pick = self.pool.get('stock.picking').browse(cr,uid,picking_id)
			res = super(order_preparation,self).picking_change(cr,uid,ids,picking_id)
			if pick:
				res['value']['partner_id'] = pick.sale_id.partner_id.id
				res['value']['partner_shipping_id'] = pick.sale_id.partner_shipping_id.id
				res['value']['poc'] = pick.sale_id.client_order_ref

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

	def send_email(self, cr, uid, ids, subject, body, follower_id, context=None):
		mail_mail = self.pool.get('mail.mail')
		mail_id = mail_mail.create(cr, uid, {
			'model': 'order.preparation',
			'res_id': ids,
			'subject': subject,
			'body_html': body,
			'auto_delete': True,
			}, context=context)
		print '============EKA CHANDRA SETIAWAN=============='

		mail_mail.send(cr, uid, [mail_id], recipient_ids=[follower_id], context=context)
		# mail_mail.send(cr, uid, [mail_id], recipient_ids=[follower_id], context=context)
		return True

	def create(self, cr, uid, vals, context=None):
		res = super(order_preparation, self).create(cr, uid, vals, context=context)
		self._set_op_followers(cr, uid, res, context=None)
		return res


	"""Action submit
	"""
	def preparation_submit(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]
		res = False
		if self.validasi(cr, uid, ids, context=context):
			res = self.write(cr, uid, ids, {'state':'submited'}, context=context)
			subject = 'Order Preparation no' + val.name + 'Submited'
			follower_id=int(592)
			body = 'Order Preparation Telah di Submited'
			self.send_email(cr, uid, ids, subject, body, follower_id, context={})
		return res

	def preparation_done(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]

		# for x in val.prepare_lines:
		# 	if x.sale_line_material_id.id==False:
		# 		raise openerp.exceptions.Warning("OP Line Tidak Memiliki ID Material Line")
		self._set_message_unread(cr, uid, ids, context=None)
		return super(order_preparation, self).preparation_done(cr, uid, ids, context=context)


	def set_delivery_notes(self, cr, uid, ids, context=None):
		res = False
		ops = self.browse(cr, uid, ids, context=context)
		dn_obj = self.pool.get('delivery.note')
		
		new_dn_ids = []
		for op in ops:
			prep_dn = {}
			evt_prepare_change = dn_obj.prepare_change(cr, uid, ids, op.id)
			print evt_prepare_change,"EVTTTTTTTT"
			prep_dn = evt_prepare_change['value']
			prep_dn['prepare_id']=op.id
			prep_dn['special']=False

			print prep_dn,"...............................,,,,,,,,,,,,,<<<<<<<<<<<<<<<"
			new_dn_ids.append(dn_obj.create(cr, uid, prep_dn, context=context))

		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ad_delivery_note', 'view_delivery_note_form')

		context.update({
			'active_model': self._name,
			'active_ids': new_dn_ids,
			'active_id': len(new_dn_ids) and new_dn_ids[0] or False
		})

		# print context,"Coooooontext"
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

		if sale:
			line = []
			data = self.pool.get('sale.order').browse(cr, uid, sale)
			
			res['poc'] = data.client_order_ref
			res['partner_id'] = data.partner_id.id
			res['duedate'] = data.delivery_date
			res['partner_shipping_id'] = data.partner_shipping_id.id

			location = []
			old_so_doc_ids = []
			for x in data.order_line:
				if x.material_lines == []:
					# raise openerp.exceptions.Warning("SO Material Belum di Definisikan")
					old_so_doc_ids.append(x.order_id.id)

			for old_id in old_so_doc_ids:
				so.generate_material(cr,uid,old_id,context=context)
				so.log(cr,uid,old_id,_('Automatic Generate Material by OP Sale Change!'))
			print data.order_line,">>>>>>>>>>>>>>>>>>>>>>>"
			for x in data.order_line:
				

				# if loc:
				# 	material_lines=so_material_line.search(cr,uid,[('sale_order_line_id', '=' ,x.id), ('picking_location', '=' , loc)])
				# else:
				# 	material_lines=so_material_line.search(cr,uid,[('sale_order_line_id', '=' ,x.id)])

				material_lines=so_material_line.search(cr,uid,[('sale_order_line_id', '=' ,x.id)])

				for y in so_material_line.browse(cr, uid, material_lines):
					print y.id,"++"
					# Cek Material Line Dengan OP Line
					nilai= 0 #nilai yang sudah di ambil item nya ke dalam op.
					op_line = []
					curr_op_id=ids

					op_line = obj_op_line.search(cr,uid,[('sale_line_material_id', '=' ,y.id),('preparation_id','not in',curr_op_id)])
					print op_line,"++--"
					for l in obj_op_line.browse(cr, uid, op_line):
						# Cek Status OP 
						op=obj_op.browse(cr, uid, [l.preparation_id.id])[0]
						product_return = 0
						search_dn_lm=obj_dn_line_mat.search(cr, uid, [('op_line_id', 'in' , [l.id])])
						print search_dn_lm,"_________________________"
						if len(search_dn_lm):
							search_cek_return=obj_dn_line_mat_ret.search(cr, uid, [('delivery_note_line_material_id', 'in' , [search_dn_lm])])
							# Cek DN Line Material Return
							for rn in obj_dn_line_mat_ret.browse(cr, uid, search_cek_return):
								if rn.stock_move_id.state == 'done':
									product_return += rn.stock_move_id.product_qty

						if op.state <> 'cancel':
							nilai += l.product_qty - product_return


					if y.product_id.type <> 'service':
						print (nilai, y.qty,'=================')
						if nilai < y.qty:
							location += [y.picking_location.id]

							line.append({
								'no': y.sale_order_line_id.sequence,
								'product_id' : y.product_id.id,
								'product_qty': y.qty - nilai, #nilai yang material line minta - op yang sudah di proses
								'product_uom': y.uom.id,
								'name': y.desc,
								'sale_line_material_id':y.id,
								'sale_line_id':y.sale_order_line_id.id
							})
			res['prepare_lines'] = line
			print res['prepare_lines'],",,,,........................................."

			# check if picking exist on Sale.Order object
			if data.picking_ids:
				# if picking ids then we need to check state
				for picking in data.picking_ids:
					active = [] #list of browse record
					if picking.state != 'cancel' or picking.state !='done':
						print "Has active picking",picking
						active.append(picking)

				if len(active)==1:
					# if only 1 active picking
					# then wee need to add picking_id into order preparation
					res['picking_id'] = active[0].id
				

			
			print res,"OP***********************************"
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
				if not re.match(r'service',product.categ_id.name,re.M|re.I):
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