import time
from datetime import date, timedelta, datetime
import netsvc
from tools.translate import _
from osv import osv, fields

class document_changes_request(osv.osv):

	_name = 'document.changes.request'

	_columns = {
		'name': fields.char('Name'),
		'request_id': fields.many2one('res.users', "Request Name",required=True),
		'reasons': fields.text('Reasons',required=True),
		'document_model': fields.many2one('ir.model', "Document Model"),
		'fk_model': fields.integer('Fk Model'),
		'document_name' : fields.char('Document Name'),
		'fault_category' : fields.selection([('user', 'User Fault'), ('external', 'External Fault'), ('system', 'System Fault')], 'Fault Category', select=True),
		'it_notes' : fields.text('IT Notes',required=False),
		'state' : fields.selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('canceled', 'Canceled'), ('rejected', 'Rejected'), ('done', 'Done')], 'State', select=True),
	}

	_inherit = ['mail.thread']
	
	def action_submit(self, cr, uid, ids, context=None):

		return self.write(cr,uid,ids,{'state':'submitted'},context=context)

	def action_approve(self, cr, uid, ids, context=None):

		return self.write(cr,uid,ids,{'state':'approved'},context=context)

	def action_reject(self, cr, uid, ids, context=None):

		return self.write(cr,uid,ids,{'state':'rejected'},context=context)

	def action_validate(self, cr, uid, ids, context=None):

		return self.write(cr,uid,ids,{'state':'done'},context=context)

	def action_open_state(self, cr, uid, ids, context=None):

		return self.write(cr,uid,ids,{'state':'draft'},context=context)

	def action_open_document(self, cr, uid, ids, context=None):

		if context is None:
			context = {}
		
		document_object = self.browse(cr,uid,ids)
		
		model_document = document_object[0].document_model.model
	
		get_document_views_id = self.pool.get('ir.ui.view').search(cr,uid,[('model', '=' , model_document), ('type', '=' , 'form'), ('inherit_id', '=' , None)])

		res = {
			'name': _(document_object[0].document_model.name),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': [get_document_views_id[0]],
			'res_model': model_document,
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'context': context,
			'res_id': document_object[0].fk_model or False,
		}

		return res

	def reqId(self, cr, uid, ids, request_id):
		if uid != request_id:
			return {'warning': {"title": _("Perhatian"), "message": _("Berubah")}, 'value': {'request_id': request_id}}
		return True	

	def _request_get(self, cr, uid, context=None):
		obj_user = self.pool.get('res.users')

		cek = obj_user.search(cr,uid,[('id', '=' ,uid)])

		if cek:
			return uid
		else:
			return False	

	_defaults = {
		'state': 'draft',
		'request_id': _request_get,
	}

document_changes_request()