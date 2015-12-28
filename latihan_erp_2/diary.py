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

class diary(osv.osv):
	_name = 'diary'
	_description = 'diary bro'
	_columns = {
		'judul':fields.char('judul'),
		'tanggal':fields.date('Date'),
		'catatan':fields.text('Catatan'),
		'state': fields.selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('cancel', 'Cancel'), ('done', 'Done')], 'State', readonly=True, select=True),		
	}



    # def diary_confirm(self, cr, uid, ids, context=None):
    #     self.write(cr, uid, ids, {'state': 'draft'})
    #     return True                                  
 
    # def diary_cancel(self, cr, uid, ids, context=None):
    #     self.write(cr, uid, ids, {'state': 'cancel'})
    #     return True       

    # def diary_validate(self, cr, uid, ids, context=None):
    #     self.write(cr, uid, ids, {'state': 'done'})
    #     return True       