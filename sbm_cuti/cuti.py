import time
from datetime import datetime
import math
import netsvc
from dateutil.relativedelta import relativedelta
from osv import osv, fields

class Remaining_Allocation(osv.osv):
	_inherit = 'hr.holidays'
	_columns = {
		'remaining':fields.integer('Remaining',size=2),
	}

	_defaults = {
        'remaining':0,
    }

	def setremaining(self,cr,uid,ids,TDays):
		return {'value':{ 'remaining':TDays} }

Remaining_Allocation()

class Form_Cuti(osv.osv):
	_inherit ='hr.holidays'
	_track = {
		'state': {
			'hr_holidays.mt_holidays_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'validate',
			'hr_holidays.mt_holidays_refused': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'refuse',
			'hr_holidays.mt_holidays_confirmed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approve_manager',
		},
	}
	_columns = {
		'alamat_cuti' : fields.char('Alamat Cuti',required=True),
		'date_from': fields.datetime('', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
		'date_to': fields.datetime('',required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
       	'hp':fields.char('Phone', size=20,required=True),
       	'note_refuse':fields.char('Note Refuse',readonly=True, states={'refuse':[('readonly',False)]}),
		'sisa_cuti':fields.integer('Remaining',size=2),
        'state': fields.selection([('draft', 'To Submit'), ('cancel', 'Cancelled'),('confirm', 'Approve'),('approve_manager', 'Approve Manager'),('approve_hrd', 'Approve HRD'), ('refuse', 'Refused'), ('validate1', 'Second Approval'), ('validate', 'Validate'),('done','Done')],
            'Status', readonly=True, track_visibility='onchange',
            help='The status is set to \'To Submit\', when a holiday request is created.\
            \nThe status is \'To Approve\', when holiday request is confirmed by user.\
            \nThe status is \'Refused\', when holiday request is refused by manager.\
            \nThe status is \'Approved\', when holiday request is approved by manager.'),
	}

	_defaults = { 'sisa_cuti':0 }
	
	def onchange_date_to(self, cr, uid, ids, date_to, date_from, Ide,IdSt):
		if (date_from and date_to) and (date_from > date_to):
			raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
		result = {'value': {}}
		if (date_to and date_from) and (date_from <= date_to):
			dayleave=0
			x = datetime.strptime(date_from,"%Y-%m-%d %H:%M:%S")
			while x <= datetime.strptime(date_to,"%Y-%m-%d %H:%M:%S"):
				if x.strftime('%A') not in ('Saturday','Sunday'):
					dayleave +=1
				x+=relativedelta(days=1)
				
			diff_day = self._get_number_of_days(date_from, date_to)
			cek=self.pool.get('hr.holidays').search(cr,uid,[('holiday_status_id', '=' ,IdSt),('employee_id', '=' ,Ide), ('remaining', '>' ,0)])
			if cek :
				hasil=self.pool.get('hr.holidays').browse(cr,uid,cek)[0]
				if hasil :
					ceksisacuti=hasil.remaining-dayleave
					if ceksisacuti < 0:
						raise osv.except_osv(('Info..!!'), ('Sisa Cuti Tidak Cukup'))
						return {'value':{ 'sisa_cuti':0, 'number_of_days_temp':0} }
					else:
						return {'value':{ 'sisa_cuti':ceksisacuti, 'number_of_days_temp':dayleave} }
		else:
			result['value']['number_of_days_temp'] = 0
		return result
	
	def holidays_validate(self, cr, uid, ids, context=None):
		self.check_holidays(cr, uid, ids, context=context)
		obj_emp = self.pool.get('hr.employee')
		ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
		manager = ids2 and ids2[0] or False
		self.write(cr, uid, ids, {'state':'done'})
		data_holiday = self.browse(cr, uid, ids)
		for record in data_holiday:
			print "a1"
			if record.sisa_cuti and record.holiday_status_id:
				print "a2",record.holiday_status_id
				hl_obj=self.search(cr,uid,[('holiday_status_id','=',record.holiday_status_id.id),('employee_id', '=' ,record.employee_id.id),('remaining', '>' ,0)])
				self.write(cr,uid,hl_obj,{'remaining':record.sisa_cuti})
				
			if record.double_validation:
				self.write(cr, uid, [record.id], {'manager_id2': manager})
			else:
				self.write(cr, uid, [record.id], {'manager_id': manager})
			if record.holiday_type == 'employee' and record.type == 'remove':
				meeting_obj = self.pool.get('crm.meeting')
				meeting_vals = {
					'name': record.name or _('Leave Request'),
					'categ_ids': record.holiday_status_id.categ_id and [(6,0,[record.holiday_status_id.categ_id.id])] or [],
					'duration': record.number_of_days_temp * 8,
					'description': record.notes,
					'user_id': record.user_id.id,
					'date': record.date_from,
					'end_date': record.date_to,
					'date_deadline': record.date_to,
					'state': 'open',			# to block that meeting date in the calendar
				}
				meeting_id = meeting_obj.create(cr, uid, meeting_vals)
				self._create_resource_leave(cr, uid, [record], context=context)
				self.write(cr, uid, ids, {'meeting_id': meeting_id})
			elif record.holiday_type == 'category':
				emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [record.category_id.id])])
				leave_ids = []
				for emp in obj_emp.browse(cr, uid, emp_ids):
					vals = {
						'name': record.name,
						'type': record.type,
						'holiday_type': 'employee',
						'holiday_status_id': record.holiday_status_id.id,
						'date_from': record.date_from,
						'date_to': record.date_to,
						'notes': record.notes,
						'number_of_days_temp': record.number_of_days_temp,
						'parent_id': record.id,
						'employee_id': emp.id
					}
					leave_ids.append(self.create(cr, uid, vals, context=None))
				wf_service = netsvc.LocalService("workflow")
				for leave_id in leave_ids:
					wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
					wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
					wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
		return True
		
	def approve_manager(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]
		usermencet = self.pool.get('res.user')
		if val.employee_id.parent_id.id != uid :
			raise osv.except_osv(('Perhatian..!!'), ('Harus Atasannya langsung ..'))
		return self.write(cr,uid,ids,{'state':'approve_hrd'})		
	
	def confirm_manager(self, cr, uid, ids, context=None):
		val = self.browse(cr, uid, ids)[0]
		usermencet = self.pool.get('res.user')
		if val.employee_id.parent_id.id != uid :
			raise osv.except_osv(('Perhatian..!!'), ('Harus Atasannya langsung ..'))
		return self.write(cr,uid,ids,{'state':'approve_hrd'})	

	def holidays_confirm(self, cr, uid, ids, context=None):
		self.check_holidays(cr, uid, ids, context=context)
		for record in self.browse(cr, uid, ids, context=context):
			if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
				self.message_subscribe_users(cr, uid, [record.id], user_ids=[record.employee_id.parent_id.user_id.id], context=context)
		return self.write(cr, uid, ids, {'state': 'confirm'})

	def holidays_first_validate(self, cr, uid, ids, context=None):
		self.check_holidays(cr, uid, ids, context=context)
		obj_emp = self.pool.get('hr.employee')
		ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
		manager = ids2 and ids2[0] or False
		self.holidays_first_validate_notificate(cr, uid, ids, context=context)
		return self.write(cr, uid, ids, {'state':'done', 'manager_id': manager})


Form_Cuti()


