from osv import osv, fields
from openerp.tools.translate import _


class force_revise_log(osv.osv):
	_name = 'forced.revise.log'
	_columns = {
		'model_id': fields.many2one('ir.model',string="Model",rerquired=True),
		'pk': fields.integer('Primary Key',required=True),
		'state_to':fields.char('State set as TO',required=True),
		'origin_state':fields.char('Origin State',required=True),
		'done':fields.boolean('Done'),
	}

	def create_for_model(self,cr,uid,model_name,vals,context={}):
		m_obj = self.pool.get('ir.model')

		m_res = m_obj.search(cr,uid,[('model','=',model_name)],context=context)
		if len(m_res)==1:
			vals['model_id'] = m_res[0]
			return self.create(cr,uid,vals,context=context)
		else:
			raise osv.excep_osv(_('Error'),_('Error to write force.revise.log'))

class sale_order(osv.osv):
	_inherit='sale.order'
	def action_force_to_draft(self,cr,uid,ids,context={}):
		for so in self.browse(cr,uid,ids,context=context):
			self.pool.get('forced.revise.log').create_for_model(cr,uid,'sale.order',{'pk':so.id,'state_to':'draft','origin_state':so.state,'done':False})
			self.write(cr,uid,ids,{'state':'draft'})