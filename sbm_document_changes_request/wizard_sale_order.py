import time
from datetime import date, timedelta, datetime
import netsvc
from tools.translate import _
from osv import osv, fields


class wizard_sale_order(osv.osv_memory):
	
	_name = "wizard.sale.order"
	
	_columns= {
		'so_id': fields.many2one('sale.order','Sale Order'),
		'wizard_so_line_ids': fields.one2many('wizard.sale.order.line', 'wizard_so_id', 'Wizard SO Line '),
	}

	def default_get(self, cr, uid, fields, context=None):
		if context is None: 
			context = {}

		active_ids = context['active_ids']
		active_model = context.get('active_model')

		res = super(wizard_sale_order, self).default_get(cr, uid, fields, context=context)
		linesData = []
		
		if active_ids and len(context['active_ids']) > 0:
			data =self.pool.get('sale.order').browse(cr,uid,active_ids[0])

			if data.order_line and len(data.order_line) > 0:
				for i in data.order_line :
					linesData += [(0,0,self._load_so_line(cr, uid, i))]

		res.update(so_id=active_ids[0])
		res.update(wizard_so_line_ids=linesData)
		return res

	def _load_so_line(self, cr, uid, line):
		so_item = {
			"so_line_id"				: line.id,
			"sequence"					: line.sequence,
		}

		return so_item

	def action_open_state(self, cr, uid, ids, context=None):
		so_object = self.pool.get('sale.order')
		so_line_object = self.pool.get('sale.order.line')
		val = self.browse(cr, uid, ids, context={})[0]

		# Update state to draft so dan so_line
		so_object.write(cr,uid,val.so_id.id,{'state':'draft', 'quotation_state':'draft'})

		for i in val.wizard_so_line_ids: 	
			if i.to_open == True:
				so_line_object.write(cr,uid,i.so_line_id.id,{'state':'draft'})

		return True


class wizard_sale_order_line(osv.osv_memory):
	
	_name = "wizard.sale.order.line"

	_columns={
		"so_line_id" : fields.many2one('sale.order.line','Sale Order Line'),
		"sequence": fields.integer('Sequence'),
		"wizard_so_id" : fields.many2one('wizard.sale.order','Wizard Sale Order'),
		"to_open": fields.boolean('to Open'),
	}