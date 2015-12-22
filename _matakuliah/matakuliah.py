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

class matakuliah(osv.osv):
	_name = 'matakuliah'
	_description = 'matakuliah'

	_columns = {
		'name':fields.char('Nama Matakuliah',required=True),
		'state':fields.selection([('draft','Draft'),('approve','Approve'),('done','Done'),('cancel','Cancel')],string="state")
		}
	_defaults={
		'state':'draft'
	}

	def write(self,cr,uid,ids,values,context=None):
		allowupdate = False
		# raise osv.except_osv(_('Error'),_('EEERRRRROOOOOR'))
		print context
		print values ,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"

		if values.get('state'):
				state_baru = values['state']
				data_sekarang = self.browse(cr,uid,ids,context=context)[0]
				if state_baru=='approve':
					if data_sekarang.state=='draft':
						allowupdate = True
				elif state_baru=='done':
					if data_sekarang.state =='approve':
						allowupdate = True
				elif state_baru=='cancel':
					if data_sekarang.state =='approve' or data_sekarang.state =='draft' :
						allowupdate = True
				elif state_baru=='draft':
					if data_sekarang.state =='approve':
						allowupdate = True
				if allowupdate:
					return super(matakuliah,self).write(cr,uid,ids,values,context=context)
					print "kebaca"
				else:

					return False
		else:
			return super(matakuliah,self).write(cr,uid,ids,values,context=context)
		
		
	# def is_allow_update_state(self,cr,uid,ids,values,context=none):


