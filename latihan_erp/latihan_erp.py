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

class absensi(osv.osv):
	_name = 'absensi'
	_description = 'absensi'
	_inherit = ['mail.thread']
	_columns = {
		'name':fields.char('Name',required=True,track_visibility="onchange"),
		'employee_id':fields.many2one('hr.employee','Employee',required=True,ondelete='cascade',onupdate='cascade'),
		
		'datetime':fields.date('Date',required=True,track_visibility="onchange"),
		
		'state':fields.selection([('draft','Draft'),('approve','Approved'),('done','Done'),('cancel','Canceled')],string="State",track_visibility="always"),
		
	}
	
	_defaults={
		'datetime':time.strftime('%Y-%m-%d'),
		'state':'draft'
	}



	def Action_Approved(self,cr,uid,ids,context={}):
		res = False
		absensi_obj = self.pool.get("absensi")
	
		if absensi_obj.write(cr,uid,ids,{'state':'approve'},context=context):
			res = True

		return res


	def Action_Done(self,cr,uid,ids,context={}):
		res = False
		absensi_obj = self.pool.get("absensi")
		if absensi_obj.write(cr,uid,ids,{'state':'done'},context=context):
			res = True

		return res

	def Action_Canceled(self,cr,uid,ids,context={}):
		res = False
		absensi_obj = self.pool.get("absensi")
		if absensi_obj.write(cr,uid,ids,{'state':'cancel'},context=context):
			res = True

		return res

	


class employeeinherit(osv.osv):
	_inherit ='hr.employee'
	_columns = {
		'log_absensi':fields.one2many('absensi','employee_id',string='Absensi'),
		
		
	}
	