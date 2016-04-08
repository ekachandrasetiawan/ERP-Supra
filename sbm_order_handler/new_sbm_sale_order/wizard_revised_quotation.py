from datetime import datetime
from stock import stock
import math
import time
import webbrowser
import netsvc
import openerp.exceptions
from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

import re

class sale_order(osv.osv):
	_inherit = 'sale.order'
	_columns = {
		'count_revised':fields.integer('Revised Time(s)',required=False),
	}
	_defaults = {
		'count_revised':0
	}
class sale_order_material_line(osv.osv):
	_name = 'sale.order.revision.history'
	_description = 'sale.order.revision.history'
	_columns = {
		'sale_order_id':fields.many2one('sale.order',required=True,string="SO"),
		'revision_reason':fields.text(string="Reason of Revision",required=True),
		'currency':fields.many2one("res.currency",string="Currency"),
		'total':fields.float(string="Total (Tax Excl)", required=True),
		'revised_on':fields.datetime(required=True)
		}
	_defaults={
			'revised_on':time.strftime('%Y-%m-%d')
		}

class wizard_revise_quotation(osv.osv_memory):
	_name ='wizard.revise.quotation'
	_columns ={
		'reason':fields.text("Reason/Explanation", required=True),
		}


	# return RFQ/16/04/00036/Rev-1
	def _setup_rev_no(self, cr, uid, ids, old_no, old_count_revised, new_count, context={}):
		new_no = old_no+'/Rev-'+str(new_count)

		if old_count_revised:
			# if had been revised before
			# RFQ/16/04/00036/Rev-1
			splited = old_no.split("Rev-")
			new_no = splited[0]+'Rev-'+str(new_count)

		print new_no,"-------------------"
		return new_no

	def confirm(self,cr,uid,ids,context={}):
		print context,'context----'
		print cr,'context----'
		print uid,'context----'
		print ids,'context----'
		res = {}

		datas_currency = self.pool.get('sale.order').browse(cr, uid,context['active_id'], context=context)

		count_revised = datas_currency.count_revised + 1

		new_revised_no = self._setup_rev_no(cr,uid,ids,datas_currency.quotation_no, datas_currency.count_revised, count_revised, context=context)

		
		# update sale order
		self.pool.get('sale.order').write(cr,uid,context['active_id'],{'quotation_state':'draft','count_revised':count_revised,'quotation_no':new_revised_no},context=context)


		datas = self.browse(cr, uid, ids[0], context=context)
		
		# create history
		self.pool.get('sale.order.revision.history').create(cr, uid,
			{ 	'sale_order_id': context['active_id'],
				'revision_reason' : datas.reason,
				'currency':datas_currency.pricelist_id.currency_id.id,
				'total':datas_currency.amount_untaxed,
				'revised_on':time.strftime('%Y-%m-%d'),

				})
		return res



