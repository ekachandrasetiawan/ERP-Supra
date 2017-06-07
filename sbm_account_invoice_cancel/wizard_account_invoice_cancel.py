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

class wizard_acount_invoice(osv.osv_memory):
	_name ='wizard.account.invoice.cancel.stage'
	_columns ={
		'cancel_reason':fields.text("Cancel Reason", required=True),
		'cancel_stage':fields.many2one('sbmcancel',string="Cancel Stage", required=False)
	}
	def confirm_(self,cr,uid,ids,context={}):
		print context,'context----'
		res = {}

		# browse() untuk mining data dari database browse(cr,uid,ids,context) ids bisa list bisa integer
		datas = self.browse(cr, uid, ids[0], context=context)
		print ids,"======================================",datas
		
		# udpate account_invoice set cancel_reason='', cancel_stage='' where account_invoice.id=id
		# self.pool.get('sale.order').write(cr,uid,context['active_id'],{'cancel_reason':datas.cancel_reason,'cancel_stage':datas.cancel_stage.id,'state':'cancel'},context=context)
		# print datas.cancel_reason




		return res

