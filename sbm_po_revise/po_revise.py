import time
import netsvc
import openerp.exceptions
from openerp.exceptions import Warning
import decimal_precision as dp
import re
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import logging

class Purchase_Order_Line(osv.osv):
	_inherit = 'purchase.order.line'
	_columns = {
		'po_line_rev': fields.many2one('purchase.order.line', 'PO Line Revise'),
	}

Purchase_Order_Line()


class Purchase_Order(osv.osv):
	_inherit = 'purchase.order'

	_columns = {
		'rev_counter':fields.integer('Rev Counter'),
		'revise_histories': fields.one2many('purchase.order.revision', 'po_source', 'Purchase Order Revision'),
		'po_revision_id': fields.many2one('purchase.order.revision', 'Purchase Order Revision'),
	}

	_defaults ={
		'rev_counter':0,
	}


	def action_invoice_create(self, cr, uid, ids, context=None):
		po_revision=self.pool.get('purchase.order.revision')
		val = self.browse(cr, uid, ids, context={})[0]

		search_po_revision = po_revision.search(cr, uid, [('po_source', '=', ids)])
		if search_po_revision:
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
		], 'Status', readonly=True, select=True, track_visibility='onchange'),
		'revise_w_new_no':fields.boolean(string='Revise New No', readonly=True, track_visibility='onchange'),
	}

	_inherit = ['mail.thread']

	_defaults = {
		'revise_w_new_no':False,
	}

	_rec_name = 'po_source'


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

	def update_revise_w_new_no(self, cr, uid, ids, context={}):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_po=self.pool.get('purchase.order')

		msg = _("Purchase Order Revision Update New Po No")
		obj_po.message_post(cr, uid, [val.po_source.id], body=msg, context=context)

		res = self.write(cr,uid,ids,{'revise_w_new_no':True},context=context)
		return res

	def po_revise_approve(self, cr, uid, ids, context={}):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_invoice = self.pool.get('account.invoice')
		obj_po = self.pool.get('purchase.order')
		obj_bank_statment = self.pool.get('account.bank.statement')
		obj_bank_statment_line = self.pool.get('account.bank.statement.line')
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
			for n in data_bank_statment:

				self.update_revise_w_new_no(cr, uid, ids, context={})
					
				msg = _("Please Cancel Bank Statement " + str(n.statement_id.name) + " --> Waiting to Cancel Bank Statement " + str(n.statement_id.name))
				obj_po.message_post(cr, uid, [val.po_source.id], body=msg, context=context)

				# elif n.statement_id.state == 'draft':
				# 	# Jika Status Masih New / Draft, Maka harus langsung Cancel
				# 	obj_bank_statment.action_cancel(cr,uid,[n.statement_id.id])
		if invoice:
			for x in obj_invoice.browse(cr, uid, invoice):
				if x.state == 'paid' or x.state == 'open':
					self.update_revise_w_new_no(cr, uid, ids, context={})

				msg = _("Waiting to Cancel Invoice " + str(x.kwitansi))
				obj_po.message_post(cr, uid, [val.po_source.id], body=msg, context=context)
				# elif x.state == 'draft':
				# 	# Jika Status Masih New / Draft, Maka harus langsung Cancel
				# 	obj_invoice.action_cancel(cr, uid, [x.id], context={})
		# return self.pool.get('warning').info(cr, uid, title='Export imformation', message="%s products Created, %s products Updated "%(str(prod_new),str(prod_update)))
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

		if val.revise_w_new_no == False:
			
			if po.po_source.name[-4:] == 'Rev'+str(val.rev_counter-1):
				seq = po.po_source.name[:-4] + 'Rev'+str(val.rev_counter)
			else:
				seq = po.po_source.name + '/Rev'+str(val.rev_counter)
		else:
			seq =int(time.time())

		po_id = obj_purchase.create(cr, uid, {
										'name':seq,
										'date_order': time.strftime("%Y-%m-%d"),
										'duedate':time.strftime("%Y-%m-%d"),
										'partner_id': po.po_source.partner_id.id,
										'jenis': po.po_source.jenis,
										'pricelist_id': po.po_source.pricelist_id.id,
										'location_id': 12,
										'origin':po.po_source.origin,
										'type_permintaan':'1',
										'term_of_payment':po.po_source.term_of_payment,
										'po_revision_id':val.id,
										'rev_counter':val.rev_counter
									   })
		noline=1
		for line in po.po_source.order_line:
			taxes = account_tax.browse(cr, uid, map(lambda line: line.id, line.product_id.supplier_taxes_id))
			fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
			taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
			obj_purchase_line.create(cr, uid, {
										 'no':noline,
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
										 'note_line':'-',
										 'taxes_id': [(6,0,taxes_ids)],
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
			if val.revise_w_new_no == False:
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


	def request_po_revise(self,cr,uid,ids,context=None):
		data = self.browse(cr,uid,ids,context)[0]
		obj_po = self.pool.get('purchase.order')
		obj_po_revision = self.pool.get('purchase.order.revision')

		data_po=obj_po.browse(cr, uid, data.po_source.id)

		po = data.po_source.id
		counter =data_po.rev_counter+1

		# Update PO Rev Counter
		obj_po.write(cr,uid,po,{'rev_counter':counter})

		# Create Stock Picking 
		po_revision = obj_po_revision.create(cr, uid, {
					'rev_counter':counter,
					'po_source':po,
					'reason':data.reason,
					'state':'confirm'
					})

		msg = _("Ask for Revision with reason: " + data.reason + " Waiting Approval")
		obj_po.message_post(cr, uid, [po], body=msg, context=context)


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
		for lines in vals['line_ids']:
			if lines[2]:
				if lines[2]['po_id']:

					po = self.pool.get('purchase.order').browse(cr, uid, [lines[2]['po_id']])[0]

					search_po_revision = po_revision.search(cr, uid, [('po_source', '=', po.id)])
					if search_po_revision:
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


	def merge_orders(self, cr, uid, ids, context={}):
		pool_data = self.pool.get('ir.model.data')
		journal_obj = self.pool.get('account.journal')
		pool_invoice = self.pool.get('account.invoice')
		pool_picking = self.pool.get('stock.picking')
		obj_po_revision=self.pool.get('purchase.order.revision')
		pool_partner = self.pool.get('res.partner')
		pool_invoice_line = self.pool.get('account.invoice.line')

		data = self.browse(cr, uid, ids, context=context)[0]
		picking_ids = [x.id for x in data['picking_ids']]
		partner_obj = data['partner_id']

		# Valisasi Invoice Picking Cek Po apakah sudah ada Invoice
		for x in picking_ids:
			pick =pool_picking.browse(cr,uid,x)

			search_po_revision = obj_po_revision.search(cr, uid, [('po_source', '=', pick.purchase_id.id)])

			if search_po_revision:
				raise osv.except_osv(_('Warning!'),
				_('Picking '+ pick.name +' dari PO ' + pick.purchase_id.name[:6] + ' Tidak Dapat Di Buat Invoice Karna Proses Revisi'))

			cr.execute("SELECT invoice_id FROM purchase_invoice_rel WHERE purchase_id = %s", [pick.purchase_id.id])
			invoice = map(lambda x: x[0], cr.fetchall())
			
			if invoice:
				raise osv.except_osv(_('Warning!'),
				_('Picking '+ pick.name +' dari PO ' + pick.purchase_id.name[:6] + ' Tidak Dapat Di Buat Invoice Dari Consolidate Picking'))


		
		alamat = pool_partner.address_get(cr, uid, [partner_obj.id],['contact', 'invoice'])
		address_contact_id = alamat['contact']
		address_invoice_id = alamat['invoice']
			   
		picking = pool_picking.browse(cr, uid, picking_ids[0], context=context)
		namepick = False
		origin = False
		if data.type == 'out':
			type_inv = 'out_invoice'
			account_id = partner_obj.property_account_receivable.id
			curency = picking.sale_id.pricelist_id.currency_id.id
			journal_ids = journal_obj.search(cr, uid, [('type','=','sale'),('company_id', '=', 1)], limit=1)


			origin = ''
			namepick = ''
			for picking in pool_picking.browse(cr, uid, picking_ids, context=context):
				if picking.note_id.id:
					origin += picking.origin +':'+ (picking.note_id.name)[:7] + ', '
				else:
					origin += picking.origin+ ', '

				namepick += picking.sale_id.client_order_ref + ', '

		elif data.type == 'in':
			type_inv = 'in_invoice'
			account_id = partner_obj.property_account_payable.id
			curency = picking.purchase_id.pricelist_id.currency_id.id
			journal_ids = journal_obj.search(cr, uid, [('type','=','purchase'),('company_id', '=', 1)], limit=1)
		
		if not journal_ids:
			raise osv.except_osv(('Error !'), ('There is no sale/purchase journal defined for this company'))            

		invoice_id = pool_invoice.create(cr, uid, {
			'name': namepick[:-2] if namepick else 'Merged Invoice for '+ partner_obj.name + ' on ' + time.strftime('%Y-%m-%d %H:%M:%S'),
			# 'name': 'Merged Invoice for '+ partner_obj.name + ' on ' + time.strftime('%Y-%m-%d %H:%M:%S'),
			'type': type_inv,
			'account_id': account_id,
			'partner_id': partner_obj.id,
			'journal_id': journal_ids[0] or False,
			'address_invoice_id': address_invoice_id,
			'address_contact_id': address_contact_id,
			'date_invoice': time.strftime('%Y-%m-%d'),
			'user_id': uid,
			'origin':origin[:-2] if origin else False,
			'currency_id': curency or False,
			'picking_ids': [(6,0, picking_ids)]})
		

		# Daftarkan Ke Purchase Invoice Rel
		add_po_id = []
		for y in picking_ids:
			pick2 =pool_picking.browse(cr,uid,y)
			add_po_id += [pick2.purchase_id.id]

		
		#convert list into set
		cek_unique = set(add_po_id)

		#convert back to list
		add_po_id = list(cek_unique)

		# Filter PO ID yang sama, Handle jika Multi Picking dari PO yang sama
		unique_list = [
		e
		for i, e in enumerate(add_po_id)
			if add_po_id.index(e) == i
		]

		for a in add_po_id:
			cr.execute('insert into purchase_invoice_rel (purchase_id,invoice_id) values (%s,%s)', (a, invoice_id))
		
		for picking in pool_picking.browse(cr, uid, picking_ids, context=context):
			pool_picking.write(cr, uid, [picking.id], {'invoice_state': 'invoiced', 'invoice_id': invoice_id}) 
			for move_line in picking.move_lines:
				disc_amount = 0
				if data.type == 'out':
					price_unit = pool_picking._get_price_unit_invoice(cr, uid, move_line, 'out_invoice')
					tax_ids = pool_picking._get_taxes_invoice(cr, uid, move_line, 'out_invoice')
					line_account_id = move_line.product_id.product_tmpl_id.property_account_income.id or move_line.product_id.categ_id.property_account_income_categ.id
				elif data.type == 'in':
					price_unit = pool_picking._get_price_unit_invoice(cr, uid, move_line, 'in_invoice')
					tax_ids = pool_picking._get_taxes_invoice(cr, uid, move_line, 'in_invoice')
					line_account_id = move_line.product_id.product_tmpl_id.property_account_expense.id or move_line.product_id.categ_id.property_account_expense_categ.id
					disc_amount = move_line.purchase_line_id.discount_nominal
				discount = pool_picking._get_discount_invoice(cr, uid, move_line)
				 
				origin = picking.origin +':'+ (picking.name).strip()
				#origin = (picking.delivery_note).strip() +';'+ (picking.name).strip()
				if picking.note_id:
					# search op line id by move line ID
					
					cekopline=self.pool.get('order.preparation.line').search(cr,uid,[('move_id', '=' ,move_line.id)])

					op_line=self.pool.get('order.preparation.line').browse(cr,uid,cekopline)
					
					if op_line:
						for opl in op_line:
							#Search DN Line ID By OP Line ID
							cek=self.pool.get('delivery.note.line').search(cr,uid,[('op_line_id', '=' ,opl.id)])
							product_dn=self.pool.get('delivery.note.line').browse(cr,uid,cek)[0]

							if cek:
								pool_invoice_line.create(
									cr, uid, 
									{
										'name': product_dn.name,
										'picking_id': picking.id,
										'origin': origin,
										'uos_id': move_line.product_uos.id or move_line.product_uom.id,
										'product_id': move_line.product_id.id,
										'price_unit': price_unit,
										'discount': discount,
										'quantity': move_line.product_qty,
										'invoice_id': invoice_id,
										'invoice_line_tax_id': [(6, 0, tax_ids)],
										'account_analytic_id': pool_picking._get_account_analytic_invoice(cr, uid, picking, move_line),
										'account_id': self.pool.get('account.fiscal.position').map_account(cr, uid, partner_obj.property_account_position, line_account_id),
										'amount_discount':disc_amount
									}
								)
							else:
								raise osv.except_osv(('Perhatian..!!'), ('No Delivery Note Tidak Ditemukan'))
						# end for
					else:
						pool_invoice_line.create(
							cr, uid, 
							{
								# 'name': picking.origin +':'+ (picking.name).strip(), #move_line.name,
								'name': move_line.name,
								'picking_id': picking.id,
								'origin': origin,
								'uos_id': move_line.product_uos.id or move_line.product_uom.id,
								'product_id': move_line.product_id.id,
								'price_unit': price_unit,
								'discount': discount,
								'quantity': move_line.product_qty,
								'invoice_id': invoice_id,
								'invoice_line_tax_id': [(6, 0, tax_ids)],
								'account_analytic_id': pool_picking._get_account_analytic_invoice(cr, uid, picking, move_line),
								'account_id': self.pool.get('account.fiscal.position').map_account(cr, uid, partner_obj.property_account_position, line_account_id),
								'amount_discount':disc_amount
							}
						)
				else:
					pool_invoice_line.create(
						cr, uid, 
						{
							# 'name': picking.origin +':'+ (picking.name).strip(), #move_line.name,
							'name': move_line.name,
							'picking_id': picking.id,
							'origin': origin,
							'uos_id': move_line.product_uos.id or move_line.product_uom.id,
							'product_id': move_line.product_id.id,
							'price_unit': price_unit,
							'discount': discount,
							'quantity': move_line.product_qty,
							'invoice_id': invoice_id,
							'invoice_line_tax_id': [(6, 0, tax_ids)],
							'account_analytic_id': pool_picking._get_account_analytic_invoice(cr, uid, picking, move_line),
							'account_id': self.pool.get('account.fiscal.position').map_account(cr, uid, partner_obj.property_account_position, line_account_id),
							'amount_discount':disc_amount
						}
					)
		pool_invoice.button_compute(cr, uid, [invoice_id], context=context, set_total=False)           
		action_model,action_id = pool_data.get_object_reference(cr, uid, 'account', "invoice_form")
		if data.type == 'in':
			action_model,action_id = pool_data.get_object_reference(cr, uid, 'account', "invoice_supplier_form")
		 
		action_pool = self.pool.get(action_model)
		res_id = action_model and action_id or False
		action = action_pool.read(cr, uid, action_id, context=context)
		action['name'] = 'Merged Invoice'
		action['view_type'] = 'form'
		action['view_mode'] = 'form'
		action['view_id'] = [res_id]
		action['res_model'] = 'account.invoice'
		action['type'] = 'ir.actions.act_window'
		action['target'] = 'current'
		action['res_id'] = invoice_id
		return action


merge_pickings()


class purchase_partial_invoice(osv.osv_memory):
	_inherit = "purchase.partial.invoice"
	
	def default_get(self, cr, uid, fields, context=None):
		po_revision=self.pool.get('purchase.order.revision')

		res = super(purchase_partial_invoice,self).default_get(cr, uid, fields, context=context)
		active_id = context.get('active_id',False)
		
		search_po_revision = po_revision.search(cr, uid, [('po_source', '=', active_id)])
		if search_po_revision:
			raise osv.except_osv(_('Warning!'),
			_('Purchase Order Tidak Dapat Di Buat Invoice Karna Proses Revisi'))

		return res

purchase_partial_invoice()