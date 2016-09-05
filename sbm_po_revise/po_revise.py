import time
import netsvc
import openerp.exceptions
import smtplib
import decimal_precision as dp
import re
import logging

from openerp.exceptions import Warning
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Purchase_Order_Line(osv.osv):
	_inherit = 'purchase.order.line'
	_columns = {
		'po_line_rev': fields.many2one('purchase.order.line', 'PO Line Revise'),
	}

Purchase_Order_Line()


class Purchase_Order(osv.osv):
	def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
		# if has default order in context
		if "default_order" in context:
			order = context['default_order']
		return super(Purchase_Order, self).search(cr, user, args, offset=offset, limit=limit, order=order, context=context, count=count)


	_inherit = 'purchase.order'

	_columns = {
		'rev_counter':fields.integer('Rev Counter'),
		'revise_histories': fields.one2many('purchase.order.revision', 'po_source', 'Purchase Order Revision'),
		'po_revision_id': fields.many2one('purchase.order.revision', 'Purchase Order Revision'),
	}

	_defaults ={
		'rev_counter':0,
	}
	
	def template_email_confirm(self, cr, uid, ids, user, no_po, url, context={}):
		res = """\
		<html>
		  <head></head>
		  <body>
		    <p>
			   	Hi %s! <br/>
				PO Revisi <b> %s </b> telah di konfirm. Silahkan follow up
		    </p>
		    <br>
		    Best Regards,<br>
			Administrator ERP
		  </body>
		</html>
		""" % (user, no_po)
		return res


	def action_invoice_create(self, cr, uid, ids, context=None):
		po_revision=self.pool.get('purchase.order.revision')
		val = self.browse(cr, uid, ids, context={})[0]

		search_po_revision = po_revision.search(cr, uid, [('po_source', '=', ids)])
		if search_po_revision:
			state_revision=po_revision.browse(cr, uid, search_po_revision)[0]
			if state_revision.state != 'cancel':
				raise osv.except_osv(_('Warning!'),
				_('Purchase Order ' + val.name + ' Tidak Dapat Di Proses Karna Revisi'))

		res = super(Purchase_Order, self).action_invoice_create(cr, uid, ids, context=None)
		return res

	def wkf_confirm_order(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		res = super(Purchase_Order, self).wkf_confirm_order(cr, uid, ids, context=None)
		return True


	def proses_po_revision(self, cr, uid, ids, po_id_revision, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_picking=self.pool.get('stock.picking')
		stock_move=self.pool.get('stock.move')
		obj_po_revision=self.pool.get('purchase.order.revision')
		obj_po_line=self.pool.get('purchase.order.line')

		po_revision = obj_po_revision.browse(cr, uid, [po_id_revision])[0]
		po_id=po_revision.po_source.id

		if val.jenis != 'impj' and val.jenis!='imps':
			# Send Email Jika Sudah Terbentuk Invoice di Purchase Order Lama
			if po_revision.is_invoiced == True:
				ip_address = '192.168.9.26:10001'
				db = 'LIVE_2014'
				url = 'http://'+ip_address+'/?db='+db+'#id=' +str(val.id)+'&view_type=form&model=purchase.order&menu_id=329&action=393'

				# Group Purhcase Manager
				m  = self.pool.get('ir.model.data')
				id_group = m.get_object(cr, uid, 'purchase', 'group_purchase_manager').id
				user_group = self.pool.get('res.groups').browse(cr, uid, id_group)

				# Group Finance Manager
				p  = self.pool.get('ir.model.data')
				finance_manager = p.get_object(cr, uid, 'account', 'group_account_manager').id
				user_finance_manager = self.pool.get('res.groups').browse(cr, uid, finance_manager)

				for x in user_group.users:
					if x.email:
						subject = 'Confirm Purchase Order Revision ' + val.name
						email_to= x.email
						template_email = self.template_email_confirm(cr, uid, ids, x.name, val.name, url, context={})
						obj_po_revision.send_email(cr, uid, ids, subject, email_to, url, template_email, context={})

				for y in user_finance_manager.users:
					if y.email:
						subject = 'Confirm Purchase Order Revision ' + val.name
						email_to= y.email
						template_email = self.template_email_confirm(cr, uid, ids, y.name, val.name, url, context={})
						obj_po_revision.send_email(cr, uid, ids, subject, email_to, url, template_email, context={})

		new_picking = obj_picking.search(cr, uid, [('purchase_id', '=', ids),(('state', '=', 'assigned'))])
		n_picking = obj_picking.browse(cr, uid, new_picking)[0]
		if n_picking:
			search_picking = obj_picking.search(cr, uid, [('purchase_id', '=', po_id)])
			picking = obj_picking.browse(cr, uid, search_picking)
			for x in picking:
				if x.state == 'done':
					#  Update Stock Pickin Doc Ref 
					obj_picking.write(cr,uid,n_picking.id,{'cust_doc_ref':x.cust_doc_ref})

					partial_data = {}
					for line in x.move_lines:
						po_line = obj_po_line.search(cr, uid, [('po_line_rev', '=', line.purchase_line_id.id)])
						po_line_id=obj_po_line.browse(cr, uid, po_line)[0]

						mv = stock_move.search(cr, uid, [('purchase_line_id', '=', po_line_id.id)])
						move_id = stock_move.browse(cr, uid, mv)[0]

						partial_data['move%s' % (move_id.id)] = {
									'product_id': line.product_id.id,
									'product_qty': line.product_qty,
									'product_uom': line.product_uom.id,
									'prodlot_id': line.prodlot_id.id}

					picking_do = obj_picking.do_partial(cr,uid,[n_picking.id],partial_data,context={})
					id_done = picking_do.items()

					# Cancel Picking State Done Old
					self.cancel_picking_done(cr, uid, x.id)
				else:
					obj_picking.action_cancel(cr, uid, [x.id])
		return True

	def action_picking_create(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_po=self.pool.get('purchase.order')
		obj_po_revision=self.pool.get('purchase.order.revision')
		
		res = super(Purchase_Order, self).action_picking_create(cr, uid, ids, context=None)

		if val.po_revision_id.id:
			self.proses_po_revision(cr, uid, ids, val.po_revision_id.id, context=None)

			# Cancel Purchase Order
			cancel_po = self.action_cancel(cr, uid, [val.po_revision_id.po_source.id], context=None)

			msg = _("Revision Version Confirmed @ " + val.name)
			obj_po.message_post(cr, uid, [val.po_revision_id.po_source.id], body=msg, context=context)

			if val.po_revision_id.po_source.state != 'cancel':
				self.cancel_purchase_order(cr, uid, [val.po_revision_id.po_source.id], context=None)

			# Done Purchase Order Revision
			obj_po_revision.write(cr,uid,val.po_revision_id.id,{'state':'done'})

		return res

	def cancel_purchase_order(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_po=self.pool.get('purchase.order')
		obj_po_line=self.pool.get('purchase.order.line')
		po=obj_po.browse(cr, uid, ids)[0]
		for x in po.order_line:
			obj_po_line.write(cr,uid,x.id,{'state':'cancel'})

		obj_po.write(cr,uid,ids,{'state':'cancel'})
		return True

	def cancel_picking_done(self, cr, uid, ids, context=None):
		obj_picking=self.pool.get('stock.picking')
		stock_move=self.pool.get('stock.move')

		pick=obj_picking.browse(cr, uid, ids)
		for x in pick.move_lines:
			stock_move.write(cr,uid,x.id,{'state':'cancel'})

		obj_picking.write(cr,uid,ids,{'state':'cancel'})

		return True
		
Purchase_Order()


class Purchase_Order_Revision(osv.osv):
	_name = 'purchase.order.revision'

	_columns = {
		'rev_counter':fields.integer('Rev Counter', readonly=True, track_visibility='onchange'),
		'po_source': fields.many2one('purchase.order', 'Purchase Order', readonly=True, track_visibility='onchange'),
		'new_po': fields.many2one('purchase.order', 'New Version', readonly=True, track_visibility='onchange'),
		'reason':fields.text('Reason', readonly=True, track_visibility='onchange'),
		'state': fields.selection([
			('confirm', 'Confirmed'),
			('approved','Approved'),
			('to_revise','To Revise'),
			('done', 'Done'),
			('cancel', 'Cancel'),
		], 'Status', readonly=True, select=True, track_visibility='onchange'),
		'is_invoiced':fields.boolean(string='Is Invoice', readonly=True, track_visibility='onchange'),
	}

	_inherit = ['mail.thread']

	_defaults = {
		'is_invoiced':False,
	}

	_rec_name = 'po_source'

	def send_email(self, cr, uid, ids, Subject, email_to, url, html, context={}):
		me="jay@beltcare.com"
		you= email_to
		msg = MIMEMultipart('alternative')
		msg['Subject'] = Subject
		msg['From'] = 'noreply@beltcare.com'
		msg['To'] = you

		part2 = MIMEText(html, 'html')

		msg.attach(part2)
		# Login Email
		username = 'jay@beltcare.com' 
		password = 'wskg3815'

		# Kirim Email
		server = smtplib.SMTP('smtp.beltcare.com:587')
		server.starttls()
		server.login(username,password)
		server.sendmail(me, you,msg.as_string())
		server.quit()
		return True

	def template_email_approve(self, cr, uid, ids, user, no_po, url, context={}):
		res = """\
		<html>
		  <head></head>
		  <body>
		    <p>
		    	Hi %s!<br><br>
				Permintaan Revisi <b>PO # %s </b> sudah di setujui.<br>
				Silahkan membuat dokumen revisi pada sistem ERP.<br>
				Klik link ini untuk membuka detail. <a href="%s">View Purchase Order Revision</a><br>
		    </p>
		    <br>
		    Best Regards,<br>
			Administrator ERP
		  </body>
		</html>
		""" % (user, no_po, url)
		return res

	def po_revision_state_cancel(self, cr, uid, ids, context={}):
		res = self.write(cr,uid,ids,{'state':'cancel'},context=context)
		return res

	def po_revision_state_setconfirm(self, cr, uid, ids, context={}):
		res = self.write(cr,uid,ids,{'state':'confirm'},context=context)
		return res

	def po_revision_state_approve(self, cr, uid, ids, context={}):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_po=self.pool.get('purchase.order')

		msg = _("Purchase Order Revision Approved")
		obj_po.message_post(cr, uid, [val.po_source.id], body=msg, context=context)
		
		res = self.write(cr,uid,ids,{'state':'approved'},context=context)
		return res

	def po_revision_state_to_revise(self, cr, uid, ids, context={}):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_po=self.pool.get('purchase.order')

		msg = _("Approval to Revision Complete")
		obj_po.message_post(cr, uid, [val.po_source.id], body=msg, context=context)

		res = self.write(cr,uid,ids,{'state':'to_revise'},context=context)
		return res

	def po_revision_state_done(self, cr, uid, ids, context={}):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_po=self.pool.get('purchase.order')

		msg = _("Purchase Order Revision Done")
		obj_po.message_post(cr, uid, [val.po_source.id], body=msg, context=context)

		res = self.write(cr,uid,ids,{'state':'done'},context=context)
		return res

	def update_is_invoiced(self, cr, uid, ids, context={}):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_po=self.pool.get('purchase.order')

		msg = _("Purchase Order Revision Update New Po No")
		obj_po.message_post(cr, uid, [val.po_source.id], body=msg, context=context)

		res = self.write(cr,uid,ids,{'is_invoiced':True},context=context)
		return res

	def check_group_purchase_manager(self, cr, uid, ids, context={}):
		#  Check User Groups Purchase Manager
		m  = self.pool.get('ir.model.data')
		id_group = m.get_object(cr, uid, 'purchase', 'group_purchase_manager').id
		user_group = self.pool.get('res.groups').browse(cr, uid, id_group)
		a = False
		for x in user_group.users:
			if x.id == uid:
				a = True

		if a == True:
			return True
		else:
			return False

	def check_group_purchase_chief(self, cr, uid, ids, context={}):
		#  Check User Groups Purchase Chief
		m  = self.pool.get('ir.model.data')
		id_group = m.get_object(cr, uid, 'sbm_po_revise', 'group_purchase_chief').id
		user_group = self.pool.get('res.groups').browse(cr, uid, id_group)
		a = False
		for x in user_group.users:
			if x.id == uid:
				a = True

		if a == True:
			return True
		else:
			return False

	def check_group_finance(self, cr, uid, ids, context={}):
		#  Jika dia Admin Invoice
		m  = self.pool.get('ir.model.data')
		id_group = m.get_object(cr, uid, 'base', 'module_category_accounting_and_finance').id
		user_group = self.pool.get('res.groups').browse(cr, uid, id_group)

		a = False
		for x in user_group.users:
			if x.id == uid:
				a = True

		if a == True:
			return True
		else:
			return False

	def po_revise_approve(self, cr, uid, ids, context={}):
		val = self.browse(cr, uid, ids, context={})[0]
		ip_address = '192.168.9.26:10001'
		db = 'LIVE_2014'
		url = 'http://'+ip_address+'/?db='+db+'#id=' +str(val.id)+'&view_type=form&model=purchase.order.revision&menu_id=738&action=892'

		obj_invoice = self.pool.get('account.invoice')
		obj_po = self.pool.get('purchase.order')
		obj_users = self.pool.get('res.users')
		obj_partner = self.pool.get('res.partner')
		obj_bank_statment = self.pool.get('account.bank.statement')
		obj_bank_statment_line = self.pool.get('account.bank.statement.line')
		obj_mail = self.pool.get('mail.followers')
		
		po_id = val.po_source.id

		#Cek Bank Statement 
		cek_po_bank = obj_bank_statment_line.search(cr, uid, [('po_id', '=', po_id)])
		data_bank_statment = obj_bank_statment_line.browse(cr, uid, cek_po_bank)

		#  Cek PO apakah sudah dibuatkan Invoice
		cr.execute("SELECT invoice_id FROM purchase_invoice_rel WHERE purchase_id = %s", [po_id])
		invoice = map(lambda x: x[0], cr.fetchall())

		if data_bank_statment == [] and invoice == []:
			self.po_revision_state_to_revise(cr, uid, ids, context={})
		else:
			self.po_revision_state_approve(cr, uid, ids, context={})
		
		if data_bank_statment:
			user_purchase_manager = self.check_group_purchase_manager(cr, uid, ids, context={})
			user_purchase_chief = self.check_group_purchase_chief(cr, uid, ids, context={})

			if user_purchase_manager == True or user_purchase_chief == True:
				user_finance = self.check_group_finance(cr, uid, ids, context={})

				if user_finance == False:
					raise osv.except_osv(('Warning..!!'), ('Akses Approve PO Revision Ada Pada Finance'))

			for n in data_bank_statment:
				self.update_is_invoiced(cr, uid, ids, context={})
					
				msg = _("Please Cancel Bank Statement " + str(n.statement_id.name) + " --> Waiting to Cancel Bank Statement " + str(n.statement_id.name))
				obj_po.message_post(cr, uid, [val.po_source.id], body=msg, context=context)

		if invoice:
			user_purchase_manager = self.check_group_purchase_manager(cr, uid, ids, context={})
			user_purchase_chief = self.check_group_purchase_chief(cr, uid, ids, context={})

			if user_purchase_manager == True or user_purchase_chief == True:
				user_finance = self.check_group_finance(cr, uid, ids, context={})

				if user_finance == False:
					raise osv.except_osv(('Warning..!!'), ('Akses Approve PO Revision Ada Pada Finance'))	

			for x in obj_invoice.browse(cr, uid, invoice):
				if x.state <> 'cancel':
					self.update_is_invoiced(cr, uid, ids, context={})

				msg = _("Waiting to Cancel Invoice " + str(x.kwitansi))
				obj_po.message_post(cr, uid, [val.po_source.id], body=msg, context=context)

		#  Saerch ID User
		cr.execute("SELECT create_uid FROM purchase_order_revision WHERE id = %s", ids)
		id_user_create = map(lambda id: id[0], cr.fetchall())


		#  Saerch Mail Followers
		cr.execute("SELECT partner_id FROM mail_followers WHERE res_model = 'purchase.order' AND res_id = %s", [po_id])
		id_mail_followers = map(lambda partner_id: partner_id[0], cr.fetchall())

		usr = obj_users.browse(cr, uid, id_user_create)[0]
		subject = 'Approve Purchase Order Revision ' + val.po_source.name
		
		po_name=val.po_source.name
		
		if val.po_source.jenis == 'loc':
			for l in id_mail_followers:
				usr = obj_partner.browse(cr, uid, [l])[0]
				for s in usr.user_ids:
					if s.email:
						email_to = s.email
						template_email = self.template_email_approve(cr, uid, ids, usr.name, po_name, url, context={})
						self.send_email(cr, uid, ids, subject, email_to, url, template_email, context={})
		return True
			
	def po_revise_setconfirmed(self, cr, uid, ids, context=None):
		res = self.po_revision_state_setconfirm(cr, uid, ids, context=None)
		return res 


	def create_purchase_order(self, cr, uid, ids,fiscal_position_id=False, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_purchase = self.pool.get('purchase.order')
		obj_purchase_line = self.pool.get('purchase.order.line')
		obj_po_revision = self.pool.get('purchase.order.revision')
		account_fiscal_position = self.pool.get('account.fiscal.position')
		account_tax = self.pool.get('account.tax')

		po = obj_po_revision.browse(cr, uid, ids)[0]

		res = {};lines= []

		if po.po_source.name[-4:] == 'Rev'+str(val.rev_counter-1):
			seq = po.po_source.name[:-4] + 'Rev'+str(val.rev_counter)
		else:
			seq = po.po_source.name + '/Rev'+str(val.rev_counter)

		po_id = obj_purchase.create(cr, uid, {
										'name':seq,
										'date_order': time.strftime("%Y-%m-%d"),
										'duedate':time.strftime("%Y-%m-%d"),
										'partner_id': po.po_source.partner_id.id,
										'attention':po.po_source.attention.id,
										'jenis': po.po_source.jenis,
										'pricelist_id': po.po_source.pricelist_id.id,
										'partner_ref': po.po_source.partner_ref,
										'location_id': po.po_source.location_id.id,
										'origin':po.po_source.origin,
										'type_permintaan':po.po_source.type_permintaan,
										'term_of_payment':po.po_source.term_of_payment,
										'company_id':po.po_source.company_id.id,
										'notes':po.po_source.notes,
										'yourref':po.po_source.yourref,
										'note':po.po_source.note,
										'other':po.po_source.other,
										'delivery':po.po_source.delivery,
										'after_shipment':po.po_source.after_shipment,
										'total_price':po.po_source.total_price,
										'shipment_to':po.po_source.shipment_to,
										'no_fpb':po.po_source.no_fpb,
										'print_line':po.po_source.print_line,
										'po_revision_id':val.id,
										'rev_counter':val.rev_counter
									   })
		noline=1
		for line in po.po_source.order_line:
			taxes = account_tax.browse(cr, uid, map(lambda line: line.id, line.product_id.supplier_taxes_id))
			fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
			taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
			if line.no:
				no_line = line.no
			else:
				no_line = noline
			if line.taxes_id:
				new_taxes = [(6,0,taxes_ids)]
			else:
				new_taxes = False
			obj_purchase_line.create(cr, uid, {
										 'no':no_line,
										 'date_planned': time.strftime("%Y-%m-%d"),
										 'order_id': po_id,
										 'product_id': line.product_id.id,
										 'variants':line.variants.id,
										 'name':line.name,
										 'part_number':line.part_number,
										 'line_pb_general_id': line.line_pb_general_id.id,
										 'product_qty': line.product_qty,
										 'product_uom': line.product_uom.id,
										 'price_unit': line.price_unit,
										 'note_line':line.note_line,
										 'discount_nominal':line.discount_nominal,
										 'discount':line.discount,
										 'move_dest_id':line.move_dest_id.id,
										 'partner_id':line.partner_id.id,
										 'company_id':line.company_id.id,
										 'line_pb_rent_id':line.line_pb_rent_id.id,
										 'line_pb_subcont_id':line.line_pb_subcont_id.id,
										 'pb_id':line.pb_id.id,
										 'wo_id':line.wo_id.id,
										 'state':'draft',
										 'taxes_id': new_taxes,
										 'po_line_rev':line.id,
										 })
			noline=noline+1
		return po_id


	def create_po(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_po = self.pool.get('purchase.order')
		obj_po_revision = self.pool.get('purchase.order.revision')
		po_id=self.create_purchase_order(cr, uid, ids, context=None)

		if val.new_po.id:
			raise osv.except_osv(('Warning..!!'), ('The New Purchase Order is Already in the Create..'))

		if po_id:
			obj_po_revision.write(cr,uid,ids,{'new_po':po_id})

			no_po = obj_po.browse(cr, uid, [po_id])[0]

			if val.po_source.name[-4:] == 'Rev'+str(val.rev_counter-1):
				name_seq = val.po_source.name[:-4] + 'Rev'+str(val.rev_counter)
			else:
				name_seq = val.po_source.name + '/Rev'+str(val.rev_counter)
					
				obj_po.write(cr,uid,po_id,{'name':name_seq})

			msg = _("Revision Version Created @ # " + no_po.name)
			obj_po.message_post(cr, uid, [val.po_source.id], body=msg, context=context)


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

Purchase_Order_Revision()

class ClassNamePOrevise(osv.osv):
	def action_po_to_revise(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		po_revision=self.pool.get('purchase.order.revision')

		search_po = po_revision.search(cr, uid, [('po_source', '=', val.id)])

		if search_po:
			state_po_revisi = po_revision.browse(cr, uid, search_po)[0]
			if state_po_revisi.state != 'cancel':
				raise osv.except_osv(('Warning..!!'), ('Purchase Order is Already in Revision..'))

		if context is None:
			context = {}
		
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_po_revise', 'wizard_po_revise_form')

		context.update({
			'active_model': self._name,
			'active_ids': ids,
			'active_id': len(ids) and ids[0] or False
		})
		return {
			'view_mode': 'form',
			'view_id': view_id,
			'view_type': 'form',
			'view_name':'wizard_po_revise_form',
			'res_model': 'wizard.po.revise',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
			'nodestroy': True,
		}

	_inherit = 'purchase.order'



class WizardPOrevise(osv.osv_memory):

	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		po_ids = context.get('active_ids', [])
		active_model = context.get('active_model')
		res = super(WizardPOrevise, self).default_get(cr, uid, fields, context=context)
		if not po_ids or len(po_ids) != 1:
			return res
		po_id, = po_ids
		if po_id:
			res.update(po_source=po_id)
			po = self.pool.get('purchase.order').browse(cr, uid, po_id, context=context)		
		return res

	def template_email_create(self, cr, uid, ids, user, user_create, no_po, notes, url, invoice, bank_statment, status, context={}):
		
		if status == False:
			res = """\
			<html>
			  <head></head>
			  <body>
			    <p>
			    	Hi %s!<br/><br/>
					%s mengajukan permohonan untuk merevisi dokumen Purchase Order <b># %s </b> <br><b>Dengan alasan :</b><br/>
					 %s .<br/><br/>
					Silahkan klik Link ini untuk melihat detail pada sistem ERP. <a href="%s">View Purchase Order Revision</a>
			    </p>
			    <br/>
			    Best Regards,<br/>
				Administrator ERP
			  </body>
			</html>
			""" % (user, user_create, no_po, notes, url)
		else:
			res = """\
			<html>
			  <head></head>
			  <body>
			    <p>
					Hi %s !<br/><br/>

					%s mengajukan permohonan untuk merevisi dokumen Purchase Order <b># %s </b> <br><b>Dengan alasan :</b><br>
					%s <br/><br/>
					PO tersebut sudah mempunyai Invoice dengan nomor kwitansi <b># %s </b> <br>

					Dan, Atau<br/>
					Mempunyai Bank Statement dengan nomor <b> %s </b><br/>
					Silahkan klik tombol Approve untuk approval permintaan tersebut pada Link ini.<a href="%s">View Purchase Order Revision</a>
			    </p>
			    <br>
			    Best Regards,<br/>
				Administrator ERP
			  </body>
			</html>
			""" % (user, user_create, no_po, notes, invoice, bank_statment, url)
		return res

	def action_send_email(self, cr, uid, ids, po_revision, po_name, user_create, notes, context=None):
		obj_invoice = self.pool.get('account.invoice')
		obj_po = self.pool.get('purchase.order')
		obj_po_revision = self.pool.get('purchase.order.revision')
		obj_users = self.pool.get('res.users')
		obj_bank_statment = self.pool.get('account.bank.statement')
		obj_bank_statment_line = self.pool.get('account.bank.statement.line')

		ip_address = '192.168.9.26:10001'
		db = 'LIVE_2014'
		url = 'http://'+ip_address+'/?db='+db+'#id=' +str(po_revision)+'&view_type=form&model=purchase.order.revision&menu_id=738&action=892'

		#Cek Bank Statement 
		cek_po_bank = obj_bank_statment_line.search(cr, uid, [('po_id', '=', ids)])
		data_bank_statment = obj_bank_statment_line.browse(cr, uid, cek_po_bank)

		#  Cek PO apakah sudah dibuatkan Invoice
		cr.execute("SELECT invoice_id FROM purchase_invoice_rel WHERE purchase_id = %s", [ids])
		invoice = map(lambda x: x[0], cr.fetchall())

		# Group Purhcase Manager
		m  = self.pool.get('ir.model.data')
		id_group = m.get_object(cr, uid, 'purchase', 'group_purchase_manager').id
		user_group = self.pool.get('res.groups').browse(cr, uid, id_group)
		
		# Group Purchase Chief
		p  = self.pool.get('ir.model.data')
		id_group_chief = p.get_object(cr, uid, 'sbm_purchase', 'group_purchase_chief').id
		user_group_chief = self.pool.get('res.groups').browse(cr, uid, id_group_chief)


		# Group Finance Manager
		p  = self.pool.get('ir.model.data')
		finance_manager = p.get_object(cr, uid, 'account', 'group_account_manager').id
		user_finance_manager = self.pool.get('res.groups').browse(cr, uid, finance_manager)


		inv =''
		bnk_statment =''

		if data_bank_statment or invoice:
			if data_bank_statment:
				for bnk in data_bank_statment:
					bnk_statment += bnk.statement_id.name +','

				bnk_statment = bnk_statment[:-1]
			if invoice:
				data_invoice = obj_invoice.browse(cr, uid, invoice)
				for i in data_invoice:
					if i.kwitansi:
						inv += i.kwitansi + ','

				inv = inv[:-1]

			# Send Email Purchase Manager
			for x in user_group.users:
				if x.email:
					subject = 'On Ask For Revision Purchase Order ' + po_name
					email_to= x.email
					template_email = self.template_email_create(cr, uid, ids, x.name, user_create, po_name, notes, url, inv, bnk_statment, status=True, context={})
					obj_po_revision.send_email(cr, uid, ids, subject, email_to, url, template_email, context={})

			# Send Email Finance Manager
			for x_finance in user_finance_manager.users:
				if x_finance.email:
					subject = 'On Ask For Revision Purchase Order ' + po_name
					email_to= x_finance.email

					template_email = self.template_email_create(cr, uid, ids, x_finance.name, user_create, po_name, notes, url, inv, bnk_statment, status=True, context={})
					obj_po_revision.send_email(cr, uid, ids, subject, email_to, url, template_email, context={})

		else:
			# Send Email Purchase Manager
			for x in user_group.users:
				if x.email:
					subject = 'On Ask For Revision Purchase Order ' + po_name
					email_to= x.email

					template_email = self.template_email_create(cr, uid, ids, x.name, user_create, po_name, notes, url, inv, bnk_statment, status=False, context={})
					obj_po_revision.send_email(cr, uid, ids, subject, email_to, url, template_email, context={})

			# Send Email Purchase Chief
			for x_chief in user_group_chief.users:
				if x_chief.email:
					subject = 'On Ask For Revision Purchase Order ' + po_name
					email_to= x_chief.email

					template_email = self.template_email_create(cr, uid, ids, x_chief.name, user_create, po_name, notes, url, inv, bnk_statment, status=False, context={})
					obj_po_revision.send_email(cr, uid, ids, subject, email_to, url, template_email, context={})
		return True

	def request_po_revise(self,cr,uid,ids,context=None):
		data = self.browse(cr,uid,ids,context)[0]
		obj_po = self.pool.get('purchase.order')
		obj_users = self.pool.get('res.users')
		obj_po_revision = self.pool.get('purchase.order.revision')
		obj_bank_statment = self.pool.get('account.bank.statement')
		obj_bank_statment_line = self.pool.get('account.bank.statement.line')

		data_po=obj_po.browse(cr, uid, data.po_source.id)

		po = data.po_source.id
		po_name = data.po_source.name
		user_create = obj_users.browse(cr, uid, uid).name
		counter =data_po.rev_counter+1
		# Update PO Rev Counter
		obj_po.write(cr,uid,po,{'rev_counter':counter})

		#Cek Bank Statement 
		cek_po_bank = obj_bank_statment_line.search(cr, uid, [('po_id', '=', po)])
		data_bank_statment = obj_bank_statment_line.browse(cr, uid, cek_po_bank)

		#  Cek PO apakah sudah dibuatkan Invoice
		cr.execute("SELECT invoice_id FROM purchase_invoice_rel WHERE purchase_id = %s", [po])
		invoice = map(lambda x: x[0], cr.fetchall())

		is_invoiced = False

		if data_bank_statment or invoice:
			is_invoiced = True
		# Create Stock Picking 
		po_revision = obj_po_revision.create(cr, uid, {
					'rev_counter':counter,
					'po_source':po,
					'reason':data.reason,
					'is_invoiced':is_invoiced,
					'state':'confirm'
					})

		msg = _("Ask for Revision with reason: " + data.reason + " Waiting Approval")
		obj_po.message_post(cr, uid, [po], body=msg, context=context)

		# Action Send Email Create Purchase Order Revision
		if data.po_source.jenis != 'impj' and data.po_source.jenis!='imps':
			self.action_send_email(cr, uid, po, po_revision, po_name, user_create, data.reason, context={})

		pool_data=self.pool.get("ir.model.data")
		action_model,action_id = pool_data.get_object_reference(cr, uid, 'sbm_po_revise', "view_po_revise_form")     
		action_pool = self.pool.get(action_model)
		res_id = action_model and action_id or False
		action = action_pool.read(cr, uid, action_id, context=context)
		action['name'] = 'purchase.order.revision.form'
		action['view_type'] = 'form'
		action['view_mode'] = 'form'
		action['view_id'] = [res_id]
		action['res_model'] = 'purchase.order.revision'
		action['type'] = 'ir.actions.act_window'
		action['target'] = 'current'
		action['res_id'] = po_revision

		return action

	_name="wizard.po.revise"
	_description="Wizard PO revise"
	_columns = {
		'po_source':fields.many2one('purchase.order',string="Purchase Order",required=True),
		'reason':fields.text('Reason',required=True,help="Reason why item(s) want to be cancel"),
	}

	_rec_name="po_source"

WizardPOrevise()




class account_invoice(osv.osv):
	_inherit = "account.invoice"

	def action_cancel(self, cr, uid, ids, context=None):
		res =super(account_invoice,self).action_cancel(cr, uid, ids, context)
		val = self.browse(cr, uid, ids, context={})[0]
		obj_invoice = self.pool.get('account.invoice')
		obj_po = self.pool.get('purchase.order')
		obj_po_revision=self.pool.get('purchase.order.revision')
		obj_bank_statment = self.pool.get('account.bank.statement')
		obj_bank_statment_line = self.pool.get('account.bank.statement.line')

		# Cek ID PO
		cr.execute("SELECT purchase_id FROM purchase_invoice_rel WHERE invoice_id = %s", ids)
		po = map(lambda x: x[0], cr.fetchall())

		cek_po_rev = obj_po_revision.search(cr, uid, [('po_source', '=', po)])
		po_rev = obj_po_revision.browse(cr, uid, cek_po_rev)

		if po_rev:
			# Cek Keseluruhan Invoice apakah sudah di cancel
			cr.execute("SELECT invoice_id FROM purchase_invoice_rel WHERE purchase_id = %s", po)
			invoice = map(lambda x: x[0], cr.fetchall())


			status_invoice = True
			for x in obj_invoice.browse(cr, uid, invoice):
				if x.state != 'cancel':
					status_invoice= False

			cek_po_bank = obj_bank_statment_line.search(cr, uid, [('po_id', '=', po)])
			data_bank_statment = obj_bank_statment_line.browse(cr, uid, cek_po_bank)

			bank_state = True
			for y in data_bank_statment:
				if y.statement_id.state != 'cancel':
					bank_state = False

			if status_invoice == True and bank_state == True:
				self.update_po_revision(cr, uid, po, context={})

		return res

	def update_po_revision(self, cr, uid, ids, context=None):
		obj_po_revision=self.pool.get('purchase.order.revision')
		obj_po=self.pool.get('purchase.order')
		cek_po = obj_po_revision.search(cr, uid, [('po_source', '=', ids)])
		data_po = obj_po_revision.browse(cr, uid, cek_po)[0]
		if data_po.state == 'approved':

			msg = _("Approval to Revision Complete")
			obj_po.message_post(cr, uid, [data_po.po_source.id], body=msg, context=context)

			return obj_po_revision.write(cr,uid,data_po.id,{'state':'to_revise'},context=context)
		else:
			return False

account_invoice()


class account_bank_statement(osv.osv):
	_inherit = "account.bank.statement"

	def create(self, cr, uid, vals, context=None):
		po_revision=self.pool.get('purchase.order.revision')
		if 'line_ids' in vals:
			for lines in vals['line_ids']:
				if lines[2]:
					if lines[2]['po_id']:

						po = self.pool.get('purchase.order').browse(cr, uid, [lines[2]['po_id']])[0]

						search_po_revision = po_revision.search(cr, uid, [('po_source', '=', po.id)])
						if search_po_revision:
							state_revision=po_revision.browse(cr, uid, search_po_revision)[0]
							if state_revision.state != 'cancel':
								raise osv.except_osv(_('Warning!'),
								_('Purchase Order ' + po.name + ' Tidak Dapat Di Proses Karna Revisi'))

		return super(account_bank_statement, self).create(cr, uid, vals, context=context)

	def action_cancel(self, cr, uid, ids, context={}):
		val = self.browse(cr, uid, ids, context={})[0]
		self.write(cr,uid,ids,{'state':'cancel'},context=context)
		status_invoice =True
		status_bank=True
		for x in val.line_ids:
			if x.po_id:
				status_invoice = self.check_state_invoice(cr, uid, x.po_id, context={})
				status_bank=self.check_state_bank(cr, uid, x.po_id, context={})

				if status_invoice == True and status_bank == True:
					self.update_po_revision(cr, uid, x.po_id.id, context={})
		return True

	def check_state_bank(self, cr, uid, ids, context={}):
		obj_bank_statment=self.pool.get('account.bank.statement')
		obj_bank_statment_line=self.pool.get('account.bank.statement.line')

		cek_po = obj_bank_statment_line.search(cr, uid, [('po_id', '=', ids.id)])
		data_bank_line = obj_bank_statment_line.browse(cr, uid, cek_po)

		status =True
		for x in data_bank_line:
			if x.statement_id.state != 'cancel':
				status = False

		return status

	def check_state_invoice(self, cr, uid, ids, context={}):
		obj_po=self.pool.get('purchase.order')
		obj_invoice=self.pool.get('account.invoice')
		obj_po_revision=self.pool.get('purchase.order.revision')
		cr.execute("SELECT invoice_id FROM purchase_invoice_rel WHERE purchase_id = %s", [ids.id])
		invoice = map(lambda x: x[0], cr.fetchall())

		status =True
		for x in invoice:
			inv = obj_invoice.browse(cr, uid, x)
			if inv.state != 'cancel':
				status=False

		return status


	def update_po_revision(self, cr, uid, ids, context=None):
		obj_po_revision=self.pool.get('purchase.order.revision')
		obj_po=self.pool.get('purchase.order')

		cek_po = obj_po_revision.search(cr, uid, [('po_source', '=', ids)])
		data_po = obj_po_revision.browse(cr, uid, cek_po)[0]
		if data_po.state == 'approved':

			msg = _("Approval to Revision Complete")
			obj_po.message_post(cr, uid, [data_po.po_source.id], body=msg, context=context)
			return obj_po_revision.write(cr,uid,data_po.id,{'state':'to_revise'},context=context)
		else:
			return False

account_bank_statement()


class purchase_partial_invoice(osv.osv_memory):
	_inherit = "purchase.partial.invoice"


purchase_partial_invoice()


class merge_pickings(osv.osv_memory):
	_inherit = "merge.pickings"

	def check_is_po_revise(self, cr, uid, ids, picking_ids, context=None):
		pool_picking = self.pool.get('stock.picking')
		obj_po_revision=self.pool.get('purchase.order.revision')
		for x in picking_ids:
			pick =pool_picking.browse(cr,uid,x)
			if pick.type == 'in':
				search_po_revision = obj_po_revision.search(cr, uid, [('po_source', '=', pick.purchase_id.id)])
				if search_po_revision:
					state_revision=obj_po_revision.browse(cr, uid, search_po_revision)[0]
					if state_revision.state != 'cancel':
						raise osv.except_osv(_('Warning!'),
						_('Picking '+ pick.name +' dari PO ' + pick.purchase_id.name[:6] + ' Tidak Dapat Di Buat Invoice Karna Proses Revisi'))

		return True


	def merge_orders(self, cr, uid, ids, context={}):
		data = self.browse(cr, uid, ids, context=context)[0]
		picking_ids = [x.id for x in data['picking_ids']]
		self.check_is_po_revise(cr, uid, ids, picking_ids)

		res = super(merge_pickings, self).merge_orders(cr, uid, ids, context=None)
		return res

merge_pickings()


class purchase_partial_invoice(osv.osv_memory):
	_inherit = "purchase.partial.invoice"
	
	def default_get(self, cr, uid, fields, context=None):
		po_revision=self.pool.get('purchase.order.revision')

		res = super(purchase_partial_invoice,self).default_get(cr, uid, fields, context=context)
		active_id = context.get('active_id',False)
		
		search_po_revision = po_revision.search(cr, uid, [('po_source', '=', active_id)])
		if search_po_revision:
			state_po = po_revision.browse(cr, uid, search_po_revision)[0]
			if state_po.state <> 'cancel':
				raise osv.except_osv(_('Warning!'),
				_('Purchase Order Tidak Dapat Di Buat Invoice Karna Proses Revisi'))

		return res

purchase_partial_invoice()