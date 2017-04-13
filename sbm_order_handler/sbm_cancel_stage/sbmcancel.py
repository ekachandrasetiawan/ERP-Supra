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

class sbmcancel(osv.osv):
	_name = 'sbmcancel'
	_description = 'sbm_cancel_stage'

	_columns = {
		
		'model_id':fields.many2one('ir.model','Model',required=True,ondelete='cascade',onupdate='cascade'),
		'name':fields.char('Name',required=True),
		'description':fields.text('Description')

	}