import time
from datetime import date, timedelta, datetime
import datetime
import netsvc
from tools.translate import _
from osv import osv, fields

class EmployeeMutasi(osv.osv):
    _inherit ='hr.employee'

    def _count_join_ages(self, cr, uid, ids, name, arg, context=None):
    	x={}
    	now = datetime.datetime.now()
    	employee= self.browse(cr, uid, ids, context=context)
    	for data in employee:
    		if data.join_on :
    			a = datetime.datetime.strptime(data.join_on, "%Y-%m-%d")
    			b = now-a
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

    			x[data.id] = str(year) + " Year " + str(bulan) + " Month " + str(hari) + " Days"
    		else:
    			x[data.id] = "-"
    	return x

    _columns = {
                'join_on':fields.date("Join w' Company"),
                'join_ages': fields.function(_count_join_ages,string="Length Of Work",type="char", store=False),
                'hr_employee_mutasi_ids': fields.one2many('hr.employee.mutasi', 'employee_id', 'History Mutasi',readonly=True),
                }


EmployeeMutasi()

class HrJob(osv.osv):
	_inherit = 'hr.job'
	_columns = {
		'is_dept_manager':fields.boolean(string='Is Dept Manager'),
	}

HrJob()

class HREmployeeMutasi(osv.osv):
	_name = 'hr.employee.mutasi'
	_columns = {
		'name':fields.char('Contract No', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'employee_id': fields.many2one('hr.employee',string="Employee",required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'type': fields.selection([
					("join","Starting Join"),
					("mutation","Mutation"),
					("promotion","Promotion"), 
					("demotion","Demotion"),
					("resign","Resign")
					],
					required=True, string="Type",readonly=True, states={'draft':[('readonly',False)]}),
		'source_department': fields.many2one('hr.department',"Source of Department", required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'source_job': fields.many2one('hr.job', "Source of Job Position", required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'destination_department': fields.many2one('hr.department', required=True, string="Destination Department",readonly=True, states={'draft':[('readonly',False)]}),
		'destination_job': fields.many2one('hr.job', required=True, string="New Job Position",readonly=True, states={'draft':[('readonly',False)]}),
		'active_on': fields.date('Active On',readonly=True, states={'draft':[('readonly',False)]}),
		'end_on': fields.date('End On',readonly=True, states={'draft':[('readonly',False)]}),
		'state': fields.selection([
					('draft','Draft'),
					('submitted','Submitted'),
					('waitingApproval1','Waiting HR Approval'),
					('waitingApproval2','Waiting GM Approval'),
					('approved','Approved'),
					('canceled','Canceled')
					], 'State'),
		'submitted_by': fields.many2one('hr.employee', "Submitted By", required=False, readonly=True),
		'approval_1_by': fields.many2one('hr.employee', "HRD Approval By", readonly=True),
		'approval_2_by': fields.many2one('hr.employee', "GM Approval By", readonly=True)
	}

	_defaults = {
		'state' : 'draft',
		'name': '/',
	}

	def create(self, cr, uid, vals, context=None):
		if vals['type'] == 'join':
			self._validateJoin(cr, uid, vals, context)
		elif vals['type'] == 'mutation':
			self._validateMutation(cr, uid, vals, context)
		elif vals['type'] == 'promotion':
			self._validatePromotion(cr, uid, vals, context)
		elif vals['type'] == 'demotion':
			self._validateDemotion(cr, uid, vals, context)
		elif vals['type'] == 'resign':
			self._validateResign(cr, uid, vals, context)
		else:
			raise osv.except_osv(('Info..!!'), ('Type Error..'))

		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.employee.mutasi.seq')
		return super(HREmployeeMutasi, self).create(cr, uid, vals, context=context)

	def submit(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'submitted'})

	def approve(self,cr,uid,ids,context=None):
		employee=self.pool.get('hr.employee').search(cr,uid,[('user_id', '=' ,uid)])
		return self.write(cr,uid,ids,{'state':'waitingApproval1','submitted_by':employee[1]})

	def waitingApproval1(self, cr, uid, ids, context=None):
		employee=self.pool.get('hr.employee').search(cr,uid,[('user_id', '=' ,uid)])
		hasil=self.pool.get('hr.employee').browse(cr,uid,employee[1])
		# if hasil.department_id.name != 'HRD' :
		# 	raise osv.except_osv(('Perhatian..!!'), ('Harus Dept HRD langsung ..'))
		# else:
		return self.write(cr,uid,ids,{'state':'waitingApproval2','approval_1_by':employee[1]})

	def waitingApproval2(self, cr, uid, ids, vals, context=None):
		hr_employee = self.pool.get('hr.employee')
		employee_mutas = self.pool.get('hr.employee.mutasi')

		mutasi = employee_mutas.browse(cr, uid, ids, context=context)[0]
		employee=self.pool.get('hr.employee').search(cr,uid,[('user_id', '=' ,uid)])
		if mutasi.type == "join":
			#  Update Master Employee
			hr_employee.write(cr, uid, mutasi.employee_id.id, {'join_on':mutasi.active_on}, context=context)

		return self.write(cr,uid,ids,{'state':'approved','approval_2_by':employee[1]})


	def _validateMutation(self,cr,uid,vals,context=None):

		return True

	def _validateDemotion(self,cr,uid,vals,context=None):

		return True

	def _validatePromotion(self,cr,uid,vals,context=None):

		return True

	def _validateJoin(self,cr,uid,vals,context=None):
		
		employee=self.pool.get('hr.employee').browse(cr,uid,vals['employee_id'])

		if employee.hr_employee_mutasi_ids:
			raise osv.except_osv(('Warning..!!'), ('Employee Sudah Terdaftar..'))
		return True

	def _validateResign(obj, cr, uid, context=None):

		return True

	# def resign(obj, cr, uid, context=None):

	# def mutation(obj, cr, uid, context=None):

	# def demotion(obj, cr, uid, context=None):

	# def promotion(obj, cr, uid, context=None):

	# def join(obj, cr, uid, context=None):


HREmployeeMutasi()