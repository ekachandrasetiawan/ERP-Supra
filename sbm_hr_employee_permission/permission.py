import time
from datetime import date, timedelta, datetime
import netsvc
from tools.translate import _
from osv import osv, fields

class HREmployeePermission(osv.osv):
	_inherit = ['mail.thread']
	_name = 'hr.employee.permission'
	_columns = {
		'name':fields.char('No',required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'employee_id':fields.many2one('hr.employee','Employee',required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'dept_id':fields.many2one('hr.department','Department',required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'affairs_type':fields.selection([('company','Company'),('personal','Personal affairs')],'Type of Affair',required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'back_to_office':fields.boolean(string='Back to Office', readonly=True, states={'draft':[('readonly',False)]}),
		'destination':fields.text('Destination', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'date_p': fields.date(string="Date",required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'time_out':fields.float('Time Out', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'time_back':fields.float('Time Back', readonly=True, states={'draft':[('readonly',False)]}),
		'security_name':fields.char('Security',size=30, readonly=True, states={'done':[('readonly',False)]}),
    	'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Check Manager'),
            ('confirm2', 'Check HRD'),
            ('done', 'Done'),
            ],
            'Status', required=True),
	}

	_defaults = {
		'state' : 'draft'
	}

	def _employee_get(obj, cr, uid, context=None):
	    if context is None:
	        context = {}
	    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
	    if ids:
	        return ids[0]
	    return False

	def _department_get(obj, cr, uid, context=None):
	    if context is None:
	        context = {}
	    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
	    if ids:
	        depds = obj.pool.get('hr.employee').browse(cr, uid, ids[0]).department_id.id
	        return depds
	    return False

	def onchange_time_out(self, cr, uid, ids, no):
		if float(no) < 23.9833333333 and float(no) > 0:
			return {'value' : {'time_out' : no}}
		else:
			return {'warning': {"title": _("Perhatian"), "message": _("Format Time Out Not Applicable")}, 'value': {'time_out': False}}

	def onchange_time_back(self, cr, uid, ids, no):
		if float(no) < 23.9833333333 and float(no) > 0:
			return {'value' : {'time_back' : no}}
		else:
			return {'warning': {"title": _("Perhatian"), "message": _("Format Time Out Not Applicable")}, 'value': {'time_back': False}}

	def dept_change(self,cr,uid,ids,pid):
		employee_id = self.pool.get('hr.employee').browse(cr,uid,pid) 
		dept_id = employee_id.department_id.id
		return {'value':{ 'dept_id':dept_id} }

	def create(self, cr, uid, vals, context=None):
		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.employee.permission.seq')
		return super(HREmployeePermission, self).create(cr, uid, vals, context=context)

	def submit(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'confirm'})

	def approve(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids)[0]
		usermencet = self.pool.get('res.user')
		if val.employee_id.parent_id.id != uid :
			raise osv.except_osv(('Perhatian..!!'), ('Harus Atasannya langsung ..'))
		return self.write(cr,uid,ids,{'state':'confirm2'})

	def validate(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids)[0]
		usermencet = self.pool.get('res.user')
		if val.employee_id.department_id.name != 'HRD' :
			raise osv.except_osv(('Perhatian..!!'), ('Harus Dept HRD langsung ..'))

		return self.write(cr,uid,ids,{'state':'done'})

	def setdraft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'draft'})

	_defaults = {
		'name': '/',
        'employee_id': _employee_get,
        'dept_id' : _department_get,
        'state': 'draft',
    }

	_track = {
		'state':{
			'sbm_hr_employee_permission.hep_confirm': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm',
			'sbm_hr_employee_permission.hep_confirm2': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm2',
			'sbm_hr_employee_permission.hep_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
			'sbm_hr_employee_permission.hep_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
		},
	}
	
HREmployeePermission()