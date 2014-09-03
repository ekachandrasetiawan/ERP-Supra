import re
import csv
import time
import base64
import calendar
from datetime import datetime
from osv import fields, osv
import decimal_precision as dp
from pkg_resources import require
from dateutil.relativedelta import relativedelta

class SalesOrderRecord(osv.osv):
    _name = "salesorderrecord.crm"
   
    _columns = {
			'periode' : fields.many2one('account.period','Periode', required=True),
			'salesman_ids' : fields.many2many('hr.employee','wizard_salesman_rel','salesman_id','wizard_id','Salesperson',required=True)
   }

    def print_report(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        x = {'ids':context.get('active_ids',[])}
        x['model'] = 'salesorderrecord.crm'
        x['form'] = self.read(cr,uid,ids)[0]
        diction = {
            'type': 'ir.actions.report.xml',
            'report_name': 'salesorderrecord.crm.form.xls',
            'report_type': 'webkit',
            'datas': x,
        }
        #print "=-===",diction
        return diction
   
SalesOrderRecord()

class SalesActivityRecord(osv.osv):
    _name = "salesactivityrecord.crm"
   
    _columns = {
            #'periode' : fields.many2one('account.period','Periode', required=True),
            'date_begin' : fields.date("Data Begin",required=True),
            'date_end' : fields.date("Date End",required=True),
            'user_ids' : fields.many2many('res.users','wizard_user_rel','user_id','wizard_id','Salesperson',required=True)
    }
    def onchange_date(self, cr, uid, ids, begin):
        if begin:
            hari = datetime.strptime(begin, "%Y-%m-%d").strftime('%A')
            if hari != 'Monday':
                raise osv.except_osv(('Attention !'), ("Begin must be Monday !"))
            ahad = datetime.strptime(begin, "%Y-%m-%d") + relativedelta(days=6)
            return {'value': {'date_end': ahad.strftime('%Y-%m-%d')}}
        return True
   

    def print_report1(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        print "----------",context
        x = {'ids':context.get('active_ids',[])}
        x['model'] = 'saleactivityrecord.crm'
        x['form'] = self.read(cr,uid,ids)[0]
        diction = {
            'type': 'ir.actions.report.xml',
            'report_name': 'salesactivityrecord.crm.form',
            'report_type': 'webkit',
            'datas': x,
        }
        #print "=-===",diction
        return diction
   
SalesActivityRecord()


class SalesProspectRecord(osv.osv):
    _name = "salesprospectrecord.crm"
   
    _columns = {
            #'periode' : fields.many2one('account.period','Periode', required=True),
#            'date_begin' : fields.date("Data Begin",required=True),
 #           'date_end' : fields.date("Date End",required=True),
	    'filter_selection' : fields.selection([('1','Customer'),('2','Product Group'),('3','Amount'),('4','Salesman')],'Filter By'),
	    'user_ids' : fields.many2many('res.users','wizard_user_rel1','user_id','wizard_id','Salesperson'),
            'customer_id' : fields.many2one('res.partner','Customer'),
            'product_group': fields.selection([('rema', 'Rema TipTop'), ('almex', 'Almex Vulcanizer '), ('crew', 'SuperScrew by Minet'), 
                                           ('uhmw', 'UHMW'), ('etec', 'Etec - Ceremic Lining'), ('ring', 'Ringfeder'), ('ohji', 'Ohji Rubber'), 
                                           ('karet', 'R/L Karet Lokal'), ('loctite', 'Loctite'), ('mbx', 'MBX Bristle Blaster'), ('3lt', '3LT'), 
                                           ('rtt', 'RTT Lining'), ('amp', 'AMP - Roady'), ('yifan', 'YIFAN - Crusher'),
                                           ('tehno', 'Tehnoroll / Ecoroll'), ('pulley', 'Tehnopulley'), ('Rulmeca', 'rulmeca'), ('lorb', 'Lorbrand'), ('voith', 'Voith'), ('trell', 'Trelleborg Marine System : Mining & Pelindo'), 
                                           ('Martin Product', 'martin'), ('tru', 'TruTrac'), ('mc', 'Mc Lanahan'), ('ball', 'Grinding Ball'), ('goodyear', 'GoodYear'), ('rocktrans', 'Rocktrans'),
                                           ('hkm', 'HKM : Magnet separator / Metal Detector'), ('ecp', 'ECP : Safety Device'), ('mti', 'Stacker Reclaimer - MTI'), ('borg', 'Trelleborg Marine System : Oil & Gas'), 
                                           ('belt', 'Belt Conveyor'), ('roler', 'Roller & Pulley')], 'Product Group'),
            'amount': fields.float('Amount', digits=(12,2)),
    }
   

    def print_report2(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        print "----------",context
        x = {'ids':context.get('active_ids',[])}
        x['model'] = 'salesprospectrecord.crm'
        x['form'] = self.read(cr,uid,ids)[0]
        diction = {
            'type': 'ir.actions.report.xml',
            'report_name': 'salesprospectrecord.crm.form',
            'report_type': 'webkit',
            'datas': x,
        }
        #print "=-===",diction
        return diction
   
SalesProspectRecord()
