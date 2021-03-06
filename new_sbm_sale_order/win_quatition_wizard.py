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

class win_quatition_wizard(osv.osv_memory):
	_name ='wizard.win.quotation'
	_columns ={
		'client_order_ref':fields.char("PO/Customer Ref No", required=True),
		'date_order':fields.date(string="Date Order", required=True),
		'due_date':fields.date(string="Due Order", required=True),
		'delivery_date':fields.date(string="Delivery Date"),
	}

	def confirm(self,cr,uid,ids,context={}):
		print context,'context----'
		res = {}

		# browse() untuk mining data dari database browse(cr,uid,ids,context) ids bisa list bisa integer
		datas = self.browse(cr, uid, ids[0], context=context)
		print ids,"======================================",datas.date_order
		if datas.date_order > datas.due_date or datas.date_order > datas.delivery_date :
			raise osv.except_osv(_('Warning'),_('Periksa Date Order, Due Date, dan Delivery Date'))

		# udpate account_invoice set cancel_reason='', cancel_stage='' where account_invoice.id=id
		self.pool.get('sale.order').write(cr,uid,context['active_id'],{'date_order':datas.date_order,'client_order_ref':datas.client_order_ref,'due_date':datas.due_date,'delivery_date':datas.delivery_date,'quotation_state':'win'},context=context)
		# print datas.cancel_reason
		quotation_obj = self.pool.get("sale.order")
		quotation_obj.action_button_confirm(cr, uid, [context['active_id']], context)
		
		return res



