import time
from datetime import date, timedelta, datetime
import netsvc
from tools.translate import _
from osv import osv, fields


class WizardPackingNotes(osv.osv_memory):
	
	_name = "wizard.packing.notes"
	
	_columns= {
		'im_id': fields.many2one('internal.move','Internal Move'),
		'packing_notes':fields.text('Packing Notes',required=False),
	}

	def default_get(self, cr, uid, fields, context=None):
		if context is None: 
			context = {}

		active_ids = context['active_ids']
		# active_model = context.get('active_model')

		res = super(WizardPackingNotes, self).default_get(cr, uid, fields, context=context)

		res.update(im_id=active_ids[0])

		return res

	def action_packing_notes(self, cr, uid, ids, context=None):
		# im_object = self.pool.get('internal.move')
		val = self.browse(cr, uid, ids, context={})[0]

		val.im_id.setAsReady({'packing_notes':val.packing_notes})

		return True