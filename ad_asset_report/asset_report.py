import re
import csv
import time
import base64
import calendar
import datetime
from osv import fields, osv

class wizard_asset_report(osv.osv_memory):
    _name = "account.assetreport"
    
    _columns = {
        'periode' : fields.many2one('account.period','Periode', required=True),
        'category_ids' : fields.many2many('account.asset.category','wizard_category_rel','category_id','wizard_id','Category',required=True),
    }
    
    def print_report(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        x = {'ids':context.get('active_ids',[])}
        x['model'] = 'account.assetreport'
        x['form'] = self.read(cr,uid,ids)[0]
        diction = {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.assetreport.xls',
            'report_type': 'webkit',
            'datas': x,
        }
        print diction
        return diction
wizard_asset_report()