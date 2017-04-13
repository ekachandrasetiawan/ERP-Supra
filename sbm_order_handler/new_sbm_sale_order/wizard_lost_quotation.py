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

class wizard_lost_quotation(osv.osv_memory):
	_name ='wizard.lost.quotation'
	_columns ={
		'reason':fields.text("Reason/Explanation", required=True),
		}

	def confirm(self,cr,uid,ids,context={}):
		print context,'context----'
		print cr,'context----'
		print uid,'context----'
		print ids,'context----'
		res = {}

		# test = self.pool.get('sale.order').browse(cr, uid, context['active_id'], context=None)

		# if test.cancel_stage:
		# 	cancel_stage = test.cancel_stage
		# else:
		# 	cancel_stage = 'internal user fault'

		# browse() untuk mining data dari database browse(cr,uid,ids,context) ids bisa list bisa integer
		datas = self.browse(cr, uid, ids[0], context=context)
		print ids,"======================================",
		

		# udpate account_invoice set cancel_reason='', cancel_stage='' where account_invoice.id=id
		self.pool.get('sale.order').write(cr,uid,context['active_id'],{'cancel_message':datas.reason,'cancel_stage':'lose','quotation_state':'lost'},context=context)
		# print datas.cancel_reason
		quotation_obj = self.pool.get("sale.order")
		quotation_obj.action_cancel(cr, uid, [context['active_id']], context)



		return res



