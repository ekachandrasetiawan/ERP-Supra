import datetime
import time
import netsvc
from openerp.tools.translate import _
from osv import osv, fields

class Purchase_Order(osv.osv):
	_inherit = 'purchase.order'

	_columns = {
		'rev_counter':fields.integer('Rev Counter'),
		'revise_history': fields.one2many('purchase.order.revision', 'po_source', 'Purchase Order Revision'),
		'po_revision_id': fields.many2one('purchase.order.revision', 'Purchase Order Revision'),
	}

	_defaults ={
		'rev_counter':0,
	}

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

	def po_resive_approve(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		obj_invoice = self.pool.get('account.invoice')
		obj_bank_statment = self.pool.get('account.bank.statement')
		obj_bank_statment_line = self.pool.get('account.bank.statement.line')
		po_id = val.po_source.id

		
		cek_po_bank = obj_bank_statment_line.search(cr, uid, [('po_id', '=', po_id)])
		data_bank_statment = obj_bank_statment_line.browse(cr, uid, cek_po_bank)

		# Cek Bank Statment 
		if data_bank_statment:
			raise osv.except_osv(_('Informasi'),_('Please Cancel DP Bank Statment'))
		else:
			#  Cek PO apakah sudah dibuatkan Invoice
			cr.execute("SELECT invoice_id FROM purchase_invoice_rel WHERE purchase_id = %s", [po_id])
			invoice = map(lambda x: x[0], cr.fetchall())

			if invoice:
				data_invoice =obj_invoice.browse(cr,uid,invoice)
				# if data_invoice.state == 'draft':
				raise osv.except_osv(_('Informasi'),_('Purchase Order Invoice Found'))

		return True

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