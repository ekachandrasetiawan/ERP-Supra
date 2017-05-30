import openerp.exceptions
import datetime,time
import os, subprocess
import json
import socket
import httplib, urllib2
import telnetlib
import xmltodict
from openerp import tools
from openerp.exceptions import Warning
from openerp.tools.translate import _
from osv import osv, fields
from xml.etree import ElementTree as ET

import logging

_logger = logging.getLogger(__name__)


class hr_attendance_type(osv.osv):
	_name = 'hr.attendance.type'
	_columns = {
		'name': fields.char('Name',required=True),
		'desc': fields.text('Desc',required=False),
		# 'notes': fields.text('Notes'),
		'is_shift_time':fields.boolean('Shift Time'),
		'employees': fields.one2many('hr.employee','attendance_type_id', required=False,string="Employees In This Attendance")
	}

class hr_attendance_non_shift_timetable(osv.osv):
	_name = 'hr.attendance.non.shift.timetable'

	_columns = {
		'att_type_id': fields.many2one('hr.attendance.type',string="Attendance Type",required=True),
		'day_index': fields.integer('Day Index',required=True),
		'name': fields.char('Day Name',required=True),
		'start_at': fields.float('Start Work At',required=True),
		'finish_work_at': fields.float('Finish Work At',required=True),
		'as_ot_day': fields.boolean('As OT Day'),

	}

class hr_employee(osv.osv):
	_inherit = 'hr.employee'
	_columns = {
		'att_pin': fields.integer(size=5,string="Attendance Machine PIN",required=False),
		'attendance_type_id': fields.many2one('hr.attendance.type',string="Attendance Type"),
		'attendance_log': fields.one2many('hr.attendance.log','employee_id', string="Attendance Log", ondelete="RESTRICT",onupdate="RESTRICT")
	}


	def get_att_pin_machine(self,cr,uid,pin,machine_ids,context={}):
		res = False
		machine_obj = self.pool.get('hr.attendance.machine')
		# machine_ids = machine_obj.search(cr,uid,[('machine_id','!=',0)])

		machines = machine_obj.browse(cr,uid,machine_ids,context=context)

		headers = {
			'Content-Type':'text/xml'
		}

		for machine in machines:
			xml = """<GetUserInfo>
				<ArgComKey Xsi:type="xsd:integer">{machine_key}</ArgComKey>
				<Arg>
					<PIN>{Pin}</PIN>
				</Arg>
			</GetUserInfo>""".format(machine_key=machine.key,Pin=pin)

			response = machine_obj._request_to_machine(cr, uid, machine.ip, headers, xml, context=context)
			print "--------------------------------",response
			log_tree = ET.fromstring(response)
			dictResponse = xmltodict.parse(response) # JSON Formatted Log from machine

			print "JSONNNNNN--->>>",dictResponse
			dictRowsResponse = dictResponse['GetUserInfoResponse']
			res = dictRowsResponse


		return res


	# upload user info into machines
	def sync_employee_into_machine(self,cr,uid,ids,context={}):
		machine_obj = self.pool.get('hr.attendance.machine')
		machine_ids = machine_obj.search(cr,uid,[('online','!=',False)])
		print "Get Machine Result -----",machine_ids,"::::::::::::::::::::::::::::::::::::::::::::"

		machines = machine_obj.browse(cr,uid,machine_ids,context=context)

		headers = {
			'Content-Type':'text/xml'
		}


		employees = self.browse(cr,uid,ids,context=context)
		exists = []
		for emp in employees:
			emp_att_pin = emp.att_pin
			for mac in machines:
				if not emp.att_pin:
					self.write(cr,uid,ids,{'att_pin':emp.id},context=context)
					emp_att_pin = emp.id
				if emp_att_pin:

					if not self.get_att_pin_machine(cr,uid,emp_att_pin,[mac.id]):
						# print "777777777777777777777777777777777777777777777777777777777777777777777"
						print "GET INNNNN ",emp_att_pin
						xml = """<SetUserInfo>
							<ArgComKey Xsi:type="xsd:integer">{machine_key}</ArgComKey>
							<Arg>
								<PIN>{Pin}</PIN>
								<Name>{Name}</Name>
							</Arg>
						</SetUserInfo>""".format(machine_key=mac.key,Pin=emp_att_pin,Name=emp.name)

						
						response = machine_obj._request_to_machine(cr, uid, mac.ip, headers, xml, context=context)
						
						log_tree = ET.fromstring(response)
						dictResponse = xmltodict.parse(response)
						print dictResponse,"XXXXXXXXXXXXXXXXXXXXXX----"
						# dictRowsResponse = dictResponse['Set']
					else:
						exs = {'machine_id':mac.id,'pin':emp_att_pin,'machine_name':mac.name}
						exists.append(exs)
					# response = machine_obj._request_to_machine(cr, uid, mac.ip, headers, xml, context=context)
				
		if exists:
			msg = 'Some machine already has user data \r\n'
			msgs = ['User pin '+str(ii['pin'])+' Exist in Machine '+ii['machine_name']+'\r\n' for ii in exists]

			msg = msg+''.join(msgs)
			print msg,"=++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
			return {'warning':{'title':'Sync Employee Data Info','message':msg}}
		return True

	def resign(self,cr,uid,ids,context={}):
		emps = self.browse(cr,uid,ids,context=context)


		machine_obj = self.pool.get('hr.attendance.machine')
		machine_ids = machine_obj._get_online_list(cr,uid)

		machines = machine_obj.browse(cr,uid,machine_ids,context=context)

		uids = []
		for emp in emps:
			if not self.delete_att_pin_machine(cr,uid,emp.att_pin,machine_ids,context=context):
				raise osv.except_osv(_('Failed!'),_('Failed to delete user on finger!'))
			if emp.user_id:
				uids.append(emp.user_id.id)
		#set as non active employee
		self.write(cr,uid,ids,{'active':False}, context=context)
		
		#set as non active users
		self.pool.get('res.users').write(cr, uid, uids, {'active':False}, context=context)

		return True

	def delete_att_pin_machine(self,cr,uid,pin,machine_ids,context={}):
		res = False
		machine_obj = self.pool.get('hr.attendance.machine')

		machines = machine_obj.browse(cr,uid,machine_ids,context=context)

		headers = {
			'Content-Type':'text/xml'
		}

		context['att_pin'] = pin
		machine_obj.stream_data_http(cr,uid,machine_ids,context=context)

		for machine in machines:

			xml = """<DeleteUser>
				<ArgComKey Xsi:type="xsd:integer">{machine_key}</ArgComKey>
				<Arg>
					<PIN>{Pin}</PIN>
				</Arg>
			</DeleteUser>""".format(machine_key=machine.key,Pin=pin)

			response = machine_obj._request_to_machine(cr, uid, machine.ip, headers, xml, context=context)
			
			log_tree = ET.fromstring(response)
			dictResponse = xmltodict.parse(response) # JSON Formatted Log from machine

			
			dictRowsResponse = dictResponse['DeleteUserResponse']['Row']['Result']
			print "DELETEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE ",dictRowsResponse
			res = True
			if dictRowsResponse != '1':
				res=False
				raise osv.except_osv(_('Error'),_('Error to delete User Info on Machine !, Please Contact system administrator'))
				


		return res

	# use for check employee id on list (integer value)
	def check_employee_ids_on_machine(self,cr,uid,ids,context={}):
		res = {}

		# res['available'] = list(self.search(cr,uid,[('att_pin','in',ids)]))
		# res['not_available'] = [eid for eid in ids if eid not in res['available']]
		print "IDS",ids
		# print 'ressssssss',self.search(cr,uid,[('att_pin','in',ids)])
		res['available'] = []
		res['not_available'] = []
		for id in ids:
			searchPin = self.search(cr,uid,[('att_pin','=',id)])
			if searchPin:
				res['available'].append(id)
			else:
				res['not_available'].append(id)
		print "---------------",res
		return res

class res_users(osv.osv):
	_inherit = 'res.users'
	_columns = {
		'admin_of_attendance_machine_ids': fields.one2many('hr.attendance.machine.admin', 'user_id',string='Admin of Attendance Machines')
	}


class hr_attendance_machine(osv.osv):
	_name = 'hr.attendance.machine'
	_columns = {
		'machine_id':fields.integer('Machine ID',required=True),
		'name': fields.char('Machine Name',required=True),
		'desc': fields.text(required=False, string="Description"),
		'ip': fields.char('IP',required=True),
		'port': fields.char('Port', required=True),
		'key': fields.char('Key',help="Key to Communicate with Machine", required=True),
		'online':fields.boolean('Online State'),
		'admin_ids':fields.one2many('hr.attendance.machine.admin','machine_id',string="Admins"),
	}
	_sql_constraints = [
		('unique_machine_id', 'unique(machine_id)', "Machine ID already defined on other machine, Machine ID must be Unique"),
	]

	def _get_online_list(self,cr,uid):
		# res = []
		return self.search(cr,uid,[('machine_id','!=','0'),('online','=',True)])

	def init_socket(self,cr,uid,ids,context={}):
		return socket.socket(socket.AF_INET,socket.SOCK_STREAM) #tcp socket

	# @return xml from xml.etree
	def _request_to_machine(self, cr, uid, machine_ip, headers, xml, context={}):
		print "XML = ====== ",xml,machine_ip
		print "HEADERSSSS ==== ",headers
		req = urllib2.Request("http://"+machine_ip+"/iWsService",data=xml,headers=headers)
		res = urllib2.urlopen(req)
		response = res.read()
		return response


	"""METHOD TO CLEAR LOG DATA
	USING stream_data_http to secure data"""
	def clear_log_data(self,cr,uid,ids,context={}):

		machines = self.browse(cr,uid,ids,context=context)
		headers = {
			'Content-Type':'text/xml'
		}
		self.stream_data_http(cr,uid,ids,context=context)
		for mac in machines:

			cmd = "<ClearData><ArgComKey xsi:type=\"xsd:integer\">"+mac.key+"</ArgComKey><Arg><Value xsi:type=\"xsd:integer\">3</Value></Arg></ClearData>"
			response = self._request_to_machine(cr, uid, mac.ip, headers, cmd, context=context)
		return True

	def _trying_connection(self,ip):
		
		try:
			print "Trying to connect "+str(ip)
			urllib2.urlopen('http://'+ip,timeout=1)
			return True
		except urllib2.URLError as err:
			print err,"---------------------------------------------------------------------------------------"
			return False


	# action to get attendance log
	def stream_data_http(self,cr,uid,ids,context={}):
		print "aaaaaaaaaaaaaaaaaaaaaaaaaaaa FETCH machine_id",ids
		Pin = context.get('att_pin','All')

		hr_employee = self.pool.get('hr.employee')

		machines = self.browse(cr,uid,ids,context=context)
		headers = {
			'Content-Type':'text/xml'
		}
		failed_connection = []
		for mac in machines:
			print mac.ip

			if not self._trying_connection(mac.ip):
				failed_connection.append({'ip':mac.ip,'name':mac.name})
				continue
				

			xml = """<GetAttLog><ArgComKey xsi:type="xsd:integer">{machine_key}</ArgComKey>
			<Arg><PIN xsi:type="xsd:integer">{Pin}</PIN></Arg></GetAttLog>""".format(machine_key=mac.key,Pin=Pin)
			
			response = self._request_to_machine(cr, uid, mac.ip, headers, xml, context=context)
			# print response,"XxXxXx-------------"
			log_tree = ET.fromstring(response)
			dictResponse = xmltodict.parse(response) # JSON Formatted Log from machine


			GetAttLogResponse = dictResponse.get('GetAttLogResponse',False)
			dictRowsResponse = False
			if GetAttLogResponse:
				dictRowsResponse = GetAttLogResponse.get('Row',False)

			# dictRowsResponse = dictResponse['GetAttLogResponse']['Row'] #[0]['PIN']
			if dictRowsResponse:
				uniq_eid = list(set(int(row['PIN']) for row in dictRowsResponse))
				
				

				check_existance_employee = hr_employee.check_employee_ids_on_machine(cr,uid,uniq_eid,context)

				flag_to_act = False # to flag is this request will be action to insert log data into OpenERP Database ?

				if not check_existance_employee['not_available']:
					# print 'All Employee is Match on OpenERP System'
					flag_to_act = True
				else:
					# if some data not sync between machine and db
					err_msg = ""
					xml_pin = ""
					for not_av in check_existance_employee['not_available']:
						xml_pin += """<Arg><PIN xsi:type="xsd:integer">{pin}</PIN></Arg>""".format(pin=not_av)
					flag_to_act = False
					xml_get_user = """<GetUserInfo>
							<ArgComKey xsi:type="xsd:integer">{machine_key}</ArgComKey>
							{PINS}
						</GetUserInfo>""".format(machine_key=mac.key,PINS=xml_pin)
					res_get_user = self._request_to_machine(cr,uid, mac.ip, headers, xml_get_user,context=context)
					dictResponseUser = xmltodict.parse(res_get_user) # JSON Formatted User INfo from machine

					if dictResponseUser['GetUserInfoResponse']:
						flag_to_act = False
						dictRowsResponseUser = dictResponseUser['GetUserInfoResponse']['Row']
					else:
						# user not exist on machine too
						dictRowsResponseUser = False
						flag_to_act = True #set flag action to True it means the log data can be inserted into OpenERP database
						print dictResponseUser['GetUserInfoResponse'],'NOt exists ----------------------------'
					if dictRowsResponseUser:
						# if many users not exits it will be response as list so we need check the data type
						if type(dictRowsResponseUser) is list:
							for uinfo in dictRowsResponseUser:
								err_msg += uinfo['Name']+" ("+uinfo['PIN2']+")\r\n"
								# print uinfo
						else:
							if dictRowsResponseUser['Name']:
								err_msg += dictRowsResponseUser['Name']+" ("+dictRowsResponseUser['PIN2']+")\r\n"
							else:
								flag_to_act = True
						if not flag_to_act:
							raise osv.except_osv(_('Processing Error!'), _('1 OR MORE EMPLOYEE DATA IS NOT EXISTS ON OPENERP SYSTEM:\r\n(%s)') \
											% (err_msg))

				# unique_eid = set(row for row in dictRowsResponse)
				att_log_obj = self.pool.get('hr.attendance.log')
				# print flag_to_act
				if flag_to_act:
					# user validation success then in this condition we must check every log are already on database or not ?
					log_to_insert = []
					for row in log_tree:
						# INDEX 0 FOR <PIN>
						# 1 FOR <DateTime>
						# 2 FOR <Verified>
						# 3 For <Status>
						# 4 For <WorkCode>
						datetime_log = int(time.mktime(time.strptime(row[1].text, '%Y-%m-%d %H:%M:%S')))
						name = time.strftime('%Y/%m')+"/"+row[0].text+"/"+str(datetime_log)
						att_pin = int(row[0].text)
						employee_id = hr_employee.search(cr,uid,[('att_pin','=',att_pin)])

						if employee_id:
							att_data = {
								'name': name,
								'employee_id': employee_id[0],
								'att_pin': att_pin,
								'datetime_log': datetime_log,
								'm_verified': row[2].text,
								'm_status': row[3].text,
								'm_work_code': row[4].text,
								'state':'3',
								'machine_id':mac.id,
							}
						# check if log already exists
						if not att_log_obj.check_is_log_exists(cr,uid,row[0].text,datetime_log,context=context):
							log_to_insert.append(att_data)
					# print log_to_insert
					# insert only the filtered log
					print log_to_insert
					att_log_obj.creates(cr,uid,log_to_insert,context=context)
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",failed_connection
		if len(failed_connection)>0:
			msg = ""
			for fail in failed_connection:
				msg += "- Machine "+fail['name']+' On IP : '+fail['ip']+'\r\n'
			raise Warning(_('Some Connection was not success to some machine.\r\nFailed to connect with :\r\n '+msg))

		return True
	def openprint_min_max(self,cr,uid,ids,context={}):
		res = False
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		url = str(browseConf.value)
		# user_ids = self.pool.get('res.users').search(cr,uid,uid,context=context)
		userBrowse = self.pool.get('res.users').browse(cr,uid,uid,context=context)
		
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_users', 'group_using_public_ip_address')
		groupBrowse = self.pool.get('res.groups').browse(cr,uid,view_id,context=context)

		# _logger.error((">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",userBrowse.employee_ids))
		employee = False
		for emp in userBrowse.employee_ids:
			employee = userBrowse.employee_ids[0]
		if employee:
			work_addr = employee.address_id.id

			for usergroup in groupBrowse.users :
				if usergroup.id == uid:
					searchConfSite = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print.public')], context=context)
					browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConfSite,context=context)[0]
					url = str(browseConf.value)

			if work_addr:			
				urlTo = url+"attendance/first-and-last-scan&site="+str(work_addr)
			else :			
				urlTo = url+"attendance/first-and-last-scan"
			
			return {
				'type'	: 'ir.actions.client',
				'target': 'new',
				'tag'	: 'print.out',
				'params': {
					# 'id'	: ids[0],
					'redir'	: urlTo
				},
			}
		else:
			raise osv.except_osv(_('Employee Null!'),_('You must be an Employee to access the page!'))
		return res

	def openprint_min_max_site(self,cr,uid,ids,context={}):
		res = False
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		url = str(browseConf.value)
		# user_ids = self.pool.get('res.users').search(cr,uid,uid,context=context)
		userBrowse = self.pool.get('res.users').browse(cr,uid,uid,context=context)

		if not userBrowse.employee_ids:
			raise Warning(_('Please contact Your System Administrator to tell this error messege!\n\nUser not related to any employee!'))
			
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_users', 'group_using_public_ip_address')
		groupBrowse = self.pool.get('res.groups').browse(cr,uid,view_id,context=context)

		employee = userBrowse.employee_ids[0]
		work_addr = employee.address_id.id

		for usergroup in groupBrowse.users :
			if usergroup.id == uid:
				searchConfSite = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print.public')], context=context)
				browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConfSite,context=context)[0]
				url = str(browseConf.value)

		if work_addr:
			urlTo = url+"attendance/first-and-last-scan-site&site="+str(work_addr)
		else :
			urlTo = url+"attendance/first-and-last-scan-site"

		
		return {
			'type'	: 'ir.actions.client',
			'target': 'new',
			'tag'	: 'print.out',
			'params': {
				# 'id'	: ids[0],
				'redir'	: urlTo
			},
		}
		return res

class hr_attendance_machine_admin(osv.osv):
	_name = 'hr.attendance.machine.admin'
	_columns = {
		'machine_id':fields.many2one('hr.attendance.machine', "Machine", required=True),
		'user_id':fields.many2one('res.users', 'User', required=True),
	}

	rec_name = "user_id"

class import_attendance_log(osv.osv):

	def cancel_import(self, cr, uid, ids, context={}):
		return self.write(cr, uid, ids, {'state':'cancel'})

	_name = 'hr.attendance.import.attendance.log'
	_columns = {
		'name':fields.char('Doc No', requried=False),
		'machine_id': fields.many2one('hr.attendance.machine',string="Machine"),
		'data':fields.binary('File',required=True),
		'state':fields.selection([('draft','Draft'),('done','Done'),('cancel','Cancel')],string="State"),
	}

	def _default_machine(self, cr, uid, context={}):
		res = False
		machine = self.pool.get('hr.attendance.machine.admin').search(cr,uid,[('user_id', '=' ,uid)])
		mac = self.pool.get('hr.attendance.machine.admin').browse(cr, uid, machine)[0]

		return mac.machine_id.id

	def _default_name(self, cr, uid, context={}):
		res_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
		initial = False
		if res_user.initial:
			initial = 'NN'
		else:
			print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< nothing initial"
		res = time.strftime('%Y/%m')+"/"+initial
		return res


	_defaults = {
		'name':_default_name,
		'state':'draft',
		'machine_id':_default_machine
	}


	# def check_is_log_exists(self,cr,uid,eid,datetime_log,context={}):

	def import_uploaded_file(self,cr,uid,ids,context={}):
		import base64
		import csv
		res = {}
		
		hr_employee = self.pool.get('hr.employee')
		hr_att_log = self.pool.get('hr.attendance.log')

		datas = self.browse(cr,uid,ids,context=context)

		for data in datas:
			updated = 0 #flag
			splited_line = (base64.decodestring(data.data).splitlines())

			splited_tab = [line.split('\t') for line in splited_line]
			data_be_inserted = []
			for spl in splited_tab:
				# loop each line SPLITED IN LIST
				# 0 = PIN
				# 1 = TIME
				# 2 - 5 STATE
				att_pin = int(spl[0])
				datetime_log = int(time.mktime(time.strptime(spl[1], '%Y-%m-%d %H:%M:%S')))


				name = time.strftime('%Y/%m')+"/"+str(att_pin)+"/"+str(datetime_log)
				employee_id = hr_employee.search(cr,uid,[('att_pin','=',att_pin)])
				
				if not hr_att_log.check_is_log_exists(cr,uid,att_pin,datetime_log,context=context) and employee_id:
					print "ATT PIN ",att_pin, " Log ",datetime_log, " Is NOTTTTTTTTTTTTTT   Exists"
					att_data = {
						'name': name,
						'employee_id': employee_id[0],
						'att_pin': att_pin,
						'datetime_log': datetime_log,
						'm_verified': spl[2],
						'm_status': spl[3],
						'm_work_code': spl[4],
						'state':'3',
						'machine_id':data.machine_id.id,
					}

					hr_att_log.create(cr,uid,att_data,context=context)
					updated = updated+1

				else:
					print "ATT PIN ",att_pin, " Log ",datetime_log, " Is Exists"
			# print data_be_inserted
			# hr_att_log.create(cr,uid,data_be_inserted,context=context)\]
			if updated:
				self.write(cr,uid,ids,{'state':'done'},context=context)
		return res


class hr_attendance_manual_reason(osv.osv):
	_name = 'hr.attendance.manual.reason'
	_columns = {
		'name': fields.char('Name',required=True),
		'desc': fields.text('Short Description',required=False),
	}


class hr_attendance_log(osv.osv):
	def _convert_date_to_epoch(self,datetime_obj):
		res = False
		res = datetime_obj.strftime('%s')
		return res
	def create(self,cr,uid,vals, context={}):
		# IF MANUAL
		if 'manual_log_time' in vals:
			# print vals['manual_log_time']
			manual_log_time = datetime.datetime.strptime(vals['manual_log_time'],'%Y-%m-%d %H:%M:%S')
			gmt7 = manual_log_time+datetime.timedelta(hours=7)
			datetime_log = self._convert_date_to_epoch(gmt7)
			if datetime_log:
				employee = self.pool.get('hr.employee').browse(cr,uid,vals['employee_id'])
				vals['datetime_log'] = datetime_log
				vals['is_manual'] = True
				vals['att_pin'] = employee.att_pin
				vals['name'] = time.strftime('%Y/%m')+"/"+str(employee.att_pin)+"/"+str(datetime_log)
				vals['state'] = '0'

				machine = self.pool.get('hr.attendance.machine').search(cr,uid,[('key','=','0')])[0]
				vals['machine_id'] = machine
			
		return super(hr_attendance_log, self).create(cr, uid, vals, context=context)
	def read(self,cr,uid,ids,fields=None, context=None, load='_classic_read'):
		if context is None:
			context = {}
		res = super(hr_attendance_log, self).read(cr,uid,ids, fields=fields, context=context, load=load)
		
		values = res
		if not isinstance(values, list):
			values = [values]
		idx = 0
		for r in values:
			# print r
			# print r['log_time'],"================================A"
			if r.__contains__('log_time') and r['log_time']:
				# print r['log_time'],"================================AAAAAAAA",idx
				log_time=datetime.datetime.strptime(r['log_time'], '%Y-%m-%d %H:%M:%S')
				print log_time
				if log_time:
					
					delta = str(log_time - datetime.timedelta(hours=7))
					print delta
					r['log_time'] = delta
					res[idx] = r
			idx = idx + 1
		# res[int(res['id'])] = r
		
		return res

	def _get_log_time_from_epoch(self, cr, uid, ids, fieldName, dict2, context=None):
		res = {}
		if context==None:
			context = {}
		print dict2
		for data in self.browse(cr,uid,ids,context):
			res[data.id] = datetime.datetime.fromtimestamp(data.datetime_log).strftime('%Y-%m-%d %H:%M:%S')
			# res[data.id] = '2015-01-01 10:30:01'
		return res

	def creates(self,cr,uid,list_vals,context={}):
		for row in list_vals:
			if self.pool.get('hr.employee').search(cr,uid,[('id','=',row['employee_id'])]):
				self.create(cr,uid,row,context=context)
		return True
	_name = 'hr.attendance.log'
	_description = 'hr attendance log'
	_columns = {
		'name':fields.char('Name',required=True),
		'employee_id': fields.many2one('hr.employee', string="Employee", required=True),
		'att_pin': fields.integer(size=5,string="Attendance PIN", required=True),
		'datetime_log': fields.integer(string="Date Time", required=True),
		'm_status': fields.selection([('0','IN'),('1','OUT/HOME'), ('2','OUT/PERMIT'), ('3','IN/PERMIT'),('4','IN/Over Time'), ('5','OUT/Over Time')], string="Machine State", required=False),
		'm_verified': fields.integer(string="Verified", required=False),
		'm_work_code': fields.integer(string="Work Code", required=False),
		'state': fields.selection([('0','Draft'), ('1','Machine Validation'), ('2', 'Need Approval'), ('3', 'Done')], string="State"),
		'is_manual': fields.boolean(string="Is Manual Input"),
		'manual_reason_id': fields.many2one('hr.attendance.manual.reason',string="Reason"),
		'manual_log_time': fields.datetime('Manual Log Time',required=False),
		'notes': fields.text(string="Notes", required=False),
		'log_time': fields.function(_get_log_time_from_epoch, method=True, string="Log Time", store=True, type="datetime"),
		'machine_id': fields.many2one('hr.attendance.machine',string='Machine ID',required=True),
		# di bawah adalah date manual
		'date_extra_out': fields.date('Date Extra Out'),
		'date_extra_in': fields.date('Date Extra In'),
		'date_in': fields.date('Date In'),
		'date_out': fields.date('Date Out'),
	}


	def update_date_manual(self, cr, uid, ids, date, aksi, context=None):

		date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
		# if aksi == 'date_extra_out':
		# 	date = date - datetime.timedelta(days=1)
		list_extra_out = self.search(cr,uid,[(aksi,'=',date)], context=context)
		# for eo in list_extra_out:
		self.write(cr, uid, ids, {'date_extra_out':None, 'date_extra_in':None, 'date_in':None, 'date_out':None},context=context)
		self.write(cr, uid, ids, {aksi:date},context=context)


		return {}

	def check_is_log_exists(self,cr,uid,eid,datetime_log,context={}):

		res = self.search(cr,uid,[('att_pin','=',eid), ('datetime_log','=',datetime_log)], context=context)
		# print "searching ",eid," and ",datetime_log
		# print res,"---------->>RES"
		return res

	def action_update_date(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids, context={})[0]
		hr=self.pool.get('hr.attendance.log')

		if context is None:
			context = {}
		
		dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sbm_hr_attendance', 'wizard_hr_attendance_form')

		context.update({
			'active_model': self._name,
			'active_ids': ids,
			'active_id': len(ids) and ids[0] or False
		})
		return {
			'view_mode': 'form',
			'view_id': view_id,
			'view_type': 'form',
			'view_name':'wizard_hr_attendance_form',
			'res_model': 'wizard.hr.attendance.log',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': context,
			'nodestroy': True,
		}

class WizardAttendanceLog(osv.osv_memory):

	def default_get(self, cr, uid, fields, context=None):
		if context is None: context = {}
		log_ids = context.get('active_ids', [])
		active_model = context.get('active_model')
		res = super(WizardAttendanceLog, self).default_get(cr, uid, fields, context=context)
		if not log_ids or len(log_ids) != 1:
			return res
		log_id, = log_ids
		if log_id:
			res.update(log_id=log_id)
			log = self.pool.get('hr.attendance.log').browse(cr, uid, log_id, context=context)	
		return res

	def update_date_hr_log(self,cr,uid,ids,context=None):
		data = self.browse(cr,uid,ids,context)[0]
		print '===================',data.log_id.id
		hr_log = self.pool.get('hr.attendance.log')
		return hr_log.write(cr,uid,data.log_id.id,{'date_extra_out':data.date_extra_out},context=context)

	_name="wizard.hr.attendance.log"
	_description="Wizard HR Attendance LOG"
	_columns = {
		'log_id':fields.many2one('hr.attendance.log',string="Attendance LOG"),
		'date_extra_out': fields.date('Date Extra Out'),
	}

WizardAttendanceLog()

class hr_attendance_min_max_log(osv.osv):
	_name = "hr.attendance.min.max.log"
	_description = "HR Attendance Min Max Log"
	_auto = False
	_columns = {
		'employee_id': fields.many2one('hr.employee',string="Employee"),
		'dept_id': fields.many2one('hr.department',string="HR Department"),
		'employee_name': fields.char('Employee Name'),
		'dept_name': fields.char('Department'),
		'y_log': fields.integer('Year'),
		'm_log': fields.integer('Month'),
		'd_log': fields.integer('Day'),
		'min_log': fields.char('Min Scanned Time'),
		'hh_min_log': fields.char('Min Hour'),
		'mm_min_log': fields.char('Min Minute'),
		'min_state_log': fields.integer('Min Time Scanned State'),
		'max_log': fields.char('Max Scanned Time'),
		'hh_max_log': fields.char('Max Hour'),
		'mm_max_log': fields.char('Max Minute'),
		'max_state_log': fields.integer('Max Time Scanned State'),
		'attendance_time': fields.char('Attendance Time'),

	}

	def init(self,cr):
		tools.sql.drop_view_if_exists(cr,'hr_attendance_min_max_log')
		cr.execute("""
		CREATE OR REPLACE VIEW hr_attendance_min_max_log AS(
			SELECT
				row_number() over() as id,
				grouped3.dept_id,
				grouped3.dept_name,
				grouped3.employee_id,
				grouped3.employee_name,
				to_date(grouped3.y_log || '-' || grouped3.m_log || '-' || grouped3.d_log, 'YYYY-MM-DD') AS full_date,
				grouped3.y_log,
				grouped3.m_log,
				grouped3.d_log,
				grouped3.dow_log,
				grouped3.scan_times_a_day,
				grouped3.min_log,
				grouped3.hh_min_log,
				grouped3.mm_min_log,
				grouped3.min_state_log,
				grouped3.max_log,
				grouped3.hh_max_log,
				grouped3.mm_max_log,
				grouped3.max_state_log,
				to_char((EXTRACT(EPOCH FROM attendance_time) || ' second')::interval, 'HH24:MI:SS') as attendance_time,
				(CASE WHEN grouped3.max_log = '-' THEN 401 ELSE 1 END) AS err_code
			FROM (
				SELECT
					grouped2.dept_id,
					grouped2.dept_name,
					grouped2.employee_id,
					grouped2.y_log,
					grouped2.m_log,
					grouped2.d_log,
					grouped2.dow_log,
					grouped2.employee_name,
					grouped2.scan_times_a_day,
					(
						CASE WHEN 
							EXTRACT(hour from grouped2.min_log) >=12 AND scan_times_a_day = 1 THEN NULL
						ELSE
							to_char(grouped2.min_log,'YYYY-MM-DD HH24:MI:SS')
						END
					) as min_log,
					
					(
						CASE WHEN 
							EXTRACT(hour from grouped2.min_log) >=12 AND scan_times_a_day = 1 THEN NULL
						ELSE
							to_char(grouped2.min_log,'HH24')
						END
					) AS hh_min_log,
					
					(
						CASE WHEN 
							EXTRACT(hour from grouped2.min_log) >=12 AND scan_times_a_day = 1 THEN NULL
						ELSE
							to_char(grouped2.min_log,'MI')
						END
					) AS MM_min_log,
					
					
					grouped2.min_state_log,
					(
						CASE WHEN grouped2.max_log = grouped2.min_log THEN 
							(
								CASE WHEN EXTRACT(hour from grouped2.min_log) >=12 AND scan_times_a_day = 1 THEN
									to_char(grouped2.max_log,'YYYY-MM-DD HH24:MI:SS') 
								ELSE
									NULL
								END
							)
						ELSE 
							to_char(grouped2.max_log,'YYYY-MM-DD HH24:MI:SS') 
						END
					) AS max_log,
					(
						CASE WHEN grouped2.max_log = grouped2.min_log THEN 
							(
								CASE WHEN EXTRACT(hour from grouped2.min_log) >=12 AND scan_times_a_day = 1 THEN
									to_char(grouped2.max_log,'HH24')
								ELSE
									NULL
								END
							)
						ELSE to_char(grouped2.max_log,'HH24') 
						END
					) AS hh_max_log,
					(
						CASE WHEN grouped2.max_log = grouped2.min_log THEN 
							(
								CASE WHEN EXTRACT(hour from grouped2.min_log) >=12 AND scan_times_a_day = 1 THEN
									to_char(grouped2.max_log,'MI')
								ELSE
									NULL
								END
							)
						ELSE 
							to_char(grouped2.max_log,'MI') 
						END
					) AS mm_max_log,
					grouped2.max_state_log,
					age(max_log,min_log) as attendance_time
				FROM
				(
					SELECT
						hdep.id as dept_id,
						hdep.name as dept_name,
						grouped1.employee_id,
						hem.name_related as employee_name,
						grouped1.y_log,
						grouped1.m_log,
						grouped1.d_log,
						grouped1.dow_log,
						(
							SELECT count(log_time) as scan_times_a_day
							FROM hr_attendance_log AS hral_min 
							WHERE hral_min.employee_id = grouped1.employee_id 
							AND EXTRACT(YEAR FROM hral_min.log_time) = grouped1.y_log 
							AND EXTRACT(MONTH FROM hral_min.log_time) = grouped1.m_log
							AND EXTRACT(DAY FROM hral_min.log_time) = grouped1.d_log
						) as scan_times_a_day,
						(
							SELECT MIN(log_time) min_log FROM hr_attendance_log AS hral_min WHERE hral_min.employee_id = grouped1.employee_id and EXTRACT(YEAR FROM hral_min.log_time) = grouped1.y_log AND EXTRACT(MONTH FROM hral_min.log_time) = grouped1.m_log AND EXTRACT(DAY FROM hral_min.log_time) = grouped1.d_log LIMIT 1
						) AS min_log,
						(
							SELECT m_status FROM hr_attendance_log AS hral_min WHERE hral_min.employee_id = grouped1.employee_id and EXTRACT(YEAR FROM hral_min.log_time) = grouped1.y_log AND EXTRACT(MONTH FROM hral_min.log_time) = grouped1.m_log AND EXTRACT(DAY FROM hral_min.log_time) = grouped1.d_log ORDER BY log_time ASC  LIMIT 1
						) AS min_state_log,
						(
							SELECT MAX(log_time) FROM hr_attendance_log AS hral_min WHERE hral_min.employee_id = grouped1.employee_id and EXTRACT(YEAR FROM hral_min.log_time) = grouped1.y_log AND EXTRACT(MONTH FROM hral_min.log_time) = grouped1.m_log AND EXTRACT(DAY FROM hral_min.log_time) = grouped1.d_log LIMIT 1
						) AS max_log,
						(
							SELECT m_status FROM hr_attendance_log AS hral_min WHERE hral_min.employee_id = grouped1.employee_id and EXTRACT(YEAR FROM hral_min.log_time) = grouped1.y_log AND EXTRACT(MONTH FROM hral_min.log_time) = grouped1.m_log AND EXTRACT(DAY FROM hral_min.log_time) = grouped1.d_log ORDER BY log_time DESC  LIMIT 1
						) AS max_state_log
					FROM
					(
						SELECT
							att_log_dec.*,
							EXTRACT(YEAR FROM att_log_dec.timestamp_log) AS y_log,
							EXTRACT(MONTH FROM att_log_dec.timestamp_log) AS m_log,
							EXTRACT(DAY FROM att_log_dec.timestamp_log) AS d_log,
							EXTRACT(DOW FROM att_log_dec.timestamp_log) AS dow_log
						FROM(
							SELECT
								id, 
								TO_TIMESTAMP(datetime_log)::TIMESTAMP WITH TIME ZONE AT TIME ZONE 'gmt+0' AS timestamp_log,
								employee_id,
								m_status
							FROM 
								hr_attendance_log
						) AS att_log_dec
					) AS grouped1
					JOIN hr_employee as hem ON grouped1.employee_id = hem.id
					JOIN hr_department as hdep ON hem.department_id = hdep.id
					GROUP BY hdep.id, hdep.name, grouped1.employee_id, hem.name_related, grouped1.y_log, grouped1.m_log, d_log, dow_log
					ORDER BY grouped1.y_log DESC, grouped1.m_log DESC, hem.name_related ASC, d_log ASC, hdep.name,  min_log DESC
				) AS grouped2
			) AS grouped3
		)""")
hr_attendance_min_max_log()


class hr_attendance_base_calendar_log(osv.osv):
	def init(self,cr):
		tools.sql.drop_view_if_exists(cr,'hr_attendance_base_calendar_log')
		cr.execute("""
			CREATE OR REPLACE VIEW hr_attendance_base_calendar_log AS ( 
				SELECT
				row_number() over() as id,
				CONCAT(e_series.i_year, '/', e_series.i_month) as ym_g,
				e_series.*,
				min_max.hh_min_log::INTEGER,
				min_max.mm_min_log::INTEGER,
				min_max.hh_max_log::INTEGER,
				min_max.mm_max_log::INTEGER,
				min_max.attendance_time
			FROM
			(
				SELECT 
					
					i_series.i,
					EXTRACT(YEAR FROM i_series.i) as i_year,
					EXTRACT(MONTH FROM i_series.i) as i_month,
					EXTRACT(DAY FROM i_series.i) as i_day,
					to_char(i_series.i, 'MONTH') AS month_name,
					to_char(i_series.i, 'DAY') as day_name,
					hr_employee.id as employee_id,
					hr_employee.name_related as employee_name,
					hr_department.name as dept_name

				FROM
				(
					SELECT i::DATE FROM generate_series('2015-06-01',NOW(), '1 day'::INTERVAL) AS i
				) AS i_series
				LEFT JOIN hr_employee ON hr_employee.attendance_type_id=1
				LEFT JOIN hr_department ON hr_employee.department_id = hr_department.id
				
			) AS e_series
			LEFT JOIN 
				hr_attendance_min_max_log AS min_max 
				ON min_max.full_date = e_series.i AND min_max.employee_id = e_series.employee_id
			ORDER BY e_series.employee_name, e_series.i
			)
		""")
	_name = 'hr.attendance.base.calendar.log'
	_description = "HR Attendance Base Calendar Log"
	_auto = False
	_columns = {
		'ym_g': fields.char('Group Year Month'),
		'i': fields.date('Date'),
		'i_year': fields.integer('Year'),
		'i_month': fields.integer('Month'),
		'i_day': fields.integer('Day'),
		'month_name': fields.char('Month Name'),
		'day_name': fields.char('Day Name'),
		'employee_id': fields.many2one('hr.employee',string="Employee"),
		'employee_name': fields.char('Employee Name'),
		'dept_name': fields.char('Dept Name'),
		'hh_min_log': fields.integer('In Hour'),
		'mm_min_log': fields.integer('In Minute'),
		'hh_max_log': fields.integer('Out Hour'),
		'mm_max_log': fields.integer('Out Minute'),
		'attendance_time': fields.char('Attendance Time')
	}