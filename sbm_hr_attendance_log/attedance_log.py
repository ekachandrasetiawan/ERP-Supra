from datetime import datetime
from stock import stock
import math
import time
import webbrowser
import netsvc
from datetime import datetime
import openerp.exceptions
from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import re

class attencance_log(osv.osv):
	_inherit = 'hr.attendance.log'
	_columns ={
		'date_extra_out': fields.date('Date Extra Out'),
		'date_extra_in': fields.date('Date Extra In'),
		'date_in': fields.date('Date In'),
		'date_out': fields.date('Date Out'),
	}

	# def unlink(cr, uid, ids, context=None):
	# 	res={}
	# 	print "testtttt"
	# 	raise osv.except_osv(_('Warning'),_('DATA TIDAK BISA DI HAPUS !!!'))
		
	# 	return super(attencance_log, self).unlink(cr, uid, ids, context=context)
	# 