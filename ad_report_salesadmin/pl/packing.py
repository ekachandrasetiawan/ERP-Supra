from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc


class packing_list_line(osv.osv):
    _inherit = "packing.list.line"
         
    def print_package(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        x = {'ids':context.get('active_ids',[])}
        x['model'] = 'packing.list.line'
        x['form'] = self.read(cr,uid,ids)[0]
        diction = {
            'type': 'ir.actions.report.xml',
            'report_name': 'pl.form.reguler',
            'report_type': 'webkit',
            'datas': x,
        }
        print "=-===",diction
        return diction
    
packing_list_line() 