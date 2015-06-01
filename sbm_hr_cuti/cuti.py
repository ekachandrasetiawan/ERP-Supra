import time
from datetime import date, timedelta, datetime
import datetime
import netsvc
from openerp import tools
from tools.translate import _
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

    # def _get_legal_leave_remaining(self, cr, uid, ids, holiday_status_id, employee_id, context=None):

    #     print '===============EkA CHANDRA ================================'

    #     return True

    _columns = {
        'holidays_addr' : fields.text('Address',required=False, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'join_ages':fields.char('Employee Join Ages',required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'date_from': fields.datetime('', readonly=True, states={'draft':[('readonly',False)]}),
        'date_to': fields.datetime('',required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'notes':fields.text('Notes',readonly=False, states={'refuse':[('readonly',False)]}),
        'current_legal_leave_remain': fields.float(string="Remaining Legal Leaves", readonly=True, states={'draft':[('readonly',False)]}),
        'manager_approved_by':fields.many2one('hr.employee', string="Manager Approval"),
        'hr_approved_by':fields.many2one('hr.employee', string="HR Approved By"),
        'state': fields.selection([
                    ('draft', 'Draft'),
                    ('cancel', 'Cancelled'),
                    ('confirm', 'To Approve'),
                    ('refuse', 'Refused'),
                    ('validate1', 'Second Approval'), 
                    ('done', 'Done')],
            'Status', readonly=True, track_visibility='onchange',
            help='The status is set to \'To Submit\', when a holiday request is created.\
            \nThe status is \'To Approve\', when holiday request is confirmed by user.\
            \nThe status is \'Refused\', when holiday request is refused by manager.\
            \nThe status is \'Approved\', when holiday request is approved by manager.'),
    }

    def onchange_employee(self, cr, uid, ids, employee_id):
        result = {'value': {'department_id': False}}
        now = datetime.datetime.now()
        hasil=self.pool.get('hr.employee').browse(cr,uid,employee_id)

        if hasil.join_on:
            a=datetime.datetime.strptime(hasil.join_on, "%Y-%m-%d")
            b=now-a
            cek = b.days / 30

            if(cek >= 12):
                year= cek/12
            else: 
                year= 0
            
            if(b.days >= 30):
                bulan = b.days/30 % 12
            else:
                bulan = 0

            hari = b.days % 30

            x = str(year) + " Year " + str(bulan) + " Month " + str(hari) + " Days"
        else:
            x = "-"

        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            result['value'] = {'department_id': employee.department_id.id, 'join_ages':x, 'current_legal_leave_remain':employee.remaining_leaves}
        return result


    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        now = datetime.datetime.now()
        a = datetime.datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
        b = a-now
        if(b.days<=7):
            return {'warning': {"title": _("Perhatian"), "message": _("The leaves application only cant applied for  7 days from now")}, 'value': {'date_from': False}}
        else:
            result = {'value':{} }
        return result


    def approve_manager(self, cr, uid, ids, context=None):
        employee=self.pool.get('hr.employee').search(cr,uid,[('user_id', '=' ,uid)])
        return self.write(cr,uid,ids,{'state':'validate1','submitted_by':employee[1]})


    def holidays_validate(self, cr, uid, ids, context=None):
        self.check_holidays(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'done'})
        data_holiday = self.browse(cr, uid, ids)
        for record in data_holiday:
            print "a1"
            # if record.sisa_cuti and record.holiday_status_id:
            #     print "a2",record.holiday_status_id
            #     hl_obj=self.search(cr,uid,[('holiday_status_id','=',record.holiday_status_id.id),('employee_id', '=' ,record.employee_id.id),('remaining', '>' ,0)])
            #     self.write(cr,uid,hl_obj,{'remaining':record.sisa_cuti})
                
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
                    'state': 'open',            # to block that meeting date in the calendar
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


Form_Cuti()


