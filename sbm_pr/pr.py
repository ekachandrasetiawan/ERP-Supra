import time
from datetime import date, timedelta, datetime
import netsvc
from openerp.tools import html_email_clean
from osv import osv, fields

class PR(osv.osv):
	_name = 'pr'
	_columns = {
		'name':fields.char('Ref No',required=True),
		'tanggal':fields.date('Date', required=True),
		'duedate':fields.date('Due Date'),
		# 'salesman_id':fields.many2one('res.users','Sales Person',required=True),
		'salesman_id': fields.many2one('res.users', "Sales Person", required=True),
        'customer_id':fields.many2one('res.partner','Customer', domain=[('customer','=',True)], required=True),
        'ref_pr':fields.char('No PR',required=True, select=True),
        'location':fields.selection([
        							('ws','Work Shop'),
        							('site','Site')],' Location Of Work',required=True),
        'notes': fields.html('Terms and Conditions'),
    	'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('done', 'Done'),
            ],
            'Status'),
    }

	def create(self, cr, uid, vals, context=None):
		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'pr')
		return super(PR, self).create(cr, uid, vals, context=context)
	def submit(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'confirm'})
	def setdraft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'draft'})
	def confirm(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'done'})

	_defaults = {
		'name': '/',
		'tanggal':time.strftime('%Y-%m-%d'),
		'state': 'draft'
	}

PR()