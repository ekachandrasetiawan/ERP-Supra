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

class account_invoice(osv.osv):
	_inherit='account.invoice'
	_columns={
		'cancel_reason':fields.text('Cancel reason'),
		'cancel_stage':fields.many2one('sbmcancel',string='Cancel Stage')
	}

