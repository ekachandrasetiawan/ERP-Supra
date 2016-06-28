import time
import netsvc
import openerp.exceptions
import decimal_precision as dp
import re
from tools.translate import _
from osv import fields, osv
from datetime import datetime, timedelta
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import logging


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

	def wkf_confirm_order(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		res = super(Purchase_Order, self).wkf_confirm_order(cr, uid, ids, context=None)

		if res:
			if val.po_revision_id.id:
				self.proses_po_revision(cr, uid, ids, val.po_revision_id.id, context=None)
		return True

	def proses_po_revision(self, cr, uid, ids, po_id_revision, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_picking=self.pool.get('stock.picking')
		obj_po_revision=self.pool.get('purchase.order.revision')

		po_revision = obj_po_revision.browse(cr, uid, [po_id_revision])[0]
		po_id=po_revision.po_source.id

		new_picking = obj_picking.search(cr, uid, [('purchase_id', '=', ids)])
		n_picking = obj_picking.browse(cr, uid, new_picking)

		for y in n_picking:
			print '===============',y.state
		if n_picking:
			print '===============adata new picking====='
			search_picking = obj_picking.search(cr, uid, [('purchase_id', '=', po_id)])
			picking = obj_picking.browse(cr, uid, search_picking)
			for x in picking:
				print '===============picking old====='
				if x.state == 'done':
					print '==============picking ada yang sudah done=====',n_picking.id
					partial_data = {}
					for line in x.move_lines:
						partial_data['move%s' % (line.id)] = {
									'product_id': line.product_id.id,
									'product_qty': line.product_qty,
									'product_uom': line.product_uom.id,
									'prodlot_id': line.prodlot_id.id}

					print '======partial dataaa=====',partial_data
					picking_do = obj_picking.do_partial(cr,uid,[n_picking.id],partial_data,context=context)
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
		res = self.write(cr,uid,ids,{'state':'approved'},context=context)
		return res

	def po_revision_state_to_revise(self, cr, uid, ids, context={}):
		res = self.write(cr,uid,ids,{'state':'to_revise'},context=context)
		return res

	def po_revision_state_done(self, cr, uid, ids, context={}):
		res = self.write(cr,uid,ids,{'state':'done'},context=context)
		return res

	def update_revise_w_new_no(self, cr, uid, ids, context={}):
		res = self.write(cr,uid,ids,{'revise_w_new_no':True},context=context)
		return res

	def po_resive_approve(self, cr, uid, ids, context={}):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_invoice = self.pool.get('account.invoice')
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
				if n.statement_id.state == 'confirm':
					self.update_revise_w_new_no(cr, uid, ids, context={})
				elif n.statement_id.state == 'draft':
					# Jika Status Masih New / Draft, Maka harus langsung Cancel
					obj_bank_statment.action_cancel(cr,uid,n.statement_id.id,context={})
		if invoice:
			for x in obj_invoice.browse(cr, uid, invoice):
				if x.state == 'paid':
					self.update_revise_w_new_no(cr, uid, ids, context={})
				elif x.state == 'draft':
					# Jika Status Masih New / Draft, Maka harus langsung Cancel
					obj_invoice.action_cancel(cr, uid, [x.id], context={})

		return True
			
	def po_resive_setconfirmed(self, cr, uid, ids, context=None):
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

		if val.revise_w_new_no == True:
			seq = po.po_source.name + '-Rev'+str(val.rev_counter)
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
										'po_revision_id':val.id
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
										 })
			noline=noline+1

		return po_id


	def create_po(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_po = self.pool.get('purchase.order')
		obj_po_revision = self.pool.get('purchase.order.revision')
		po_id=self.create_purchase_order(cr, uid, ids, context=None)

		if po_id:
			obj_po_revision.write(cr,uid,ids,{'new_po':po_id})

			if val.revise_w_new_no == True:
				name_seq = val.po_source.name + '-Rev'+str(val.rev_counter)
				obj_po.write(cr,uid,po_id,{'name':name_seq})

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

class ClassNamePOResive(osv.osv):
	def action_po_to_revise(self,cr,uid,ids,context=None):
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
			'res_model': 'wizard.po.resive',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
			'nodestroy': True,
		}
	_inherit = 'purchase.order'



class WizardPOResive(osv.osv_memory):

	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		po_ids = context.get('active_ids', [])
		active_model = context.get('active_model')
		res = super(WizardPOResive, self).default_get(cr, uid, fields, context=context)
		if not po_ids or len(po_ids) != 1:
			return res
		po_id, = po_ids
		if po_id:
			res.update(po_source=po_id)
			po = self.pool.get('purchase.order').browse(cr, uid, po_id, context=context)		
		return res


	def request_po_resive(self,cr,uid,ids,context=None):
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

		# redir

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

	_name="wizard.po.resive"
	_description="Wizard PO Resive"
	_columns = {
		'po_source':fields.many2one('purchase.order',string="Purchase Order",required=True),
		'reason':fields.text('Reason',required=True,help="Reason why item(s) want to be cancel"),
	}

	_rec_name="po_source"

WizardPOResive()




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

		cek_po = obj_po_revision.search(cr, uid, [('po_source', '=', ids)])
		data_po = obj_po_revision.browse(cr, uid, cek_po)[0]
		if data_po.state == 'approved':
			return obj_po_revision.write(cr,uid,data_po.id,{'state':'to_revise'},context=context)
		else:
			return False


account_invoice()

class account_bank_statement(osv.osv):
	_inherit = "account.bank.statement"

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

		cek_po = obj_po_revision.search(cr, uid, [('po_source', '=', ids)])
		data_po = obj_po_revision.browse(cr, uid, cek_po)[0]
		if data_po.state == 'approved':
			return obj_po_revision.write(cr,uid,data_po.id,{'state':'to_revise'},context=context)
		else:
			return False

account_bank_statement()