import openerp.exceptions
import datetime,time
import os, subprocess
import json
import socket
import httplib, urllib2
import telnetlib
import requests
import xmltodict
from openerp import tools
from openerp.tools.translate import _
from osv import osv, fields
from xml.etree import ElementTree as ET

class hr_employee(osv.osv):
	_inherit = 'hr.employee'
	_columns = {
		'att_pin': fields.integer(size=5,string="Attendance Machine PIN",required=False),
	}

	# use for check employee id on list (integer value)
	def check_employee_ids_on_machine(self,cr,uid,ids,context={}):
		res = {}

		res['available'] = list(self.search(cr,uid,[('att_pin','in',ids)]))
		res['not_available'] = [eid for eid in ids if eid not in res['available']]
		print res
		return res

class hr_attendance_machine(osv.osv):
	_name = 'hr.attendance.machine'
	_columns = {
		'machine_id':fields.integer('Machine ID',required=True),
		'name': fields.char('Machine Name',required=True),
		'desc': fields.text(required=False, string="Description"),
		'ip': fields.char('IP',required=True),
		'port': fields.char('Port', required=True),
		'key': fields.char('Key',help="Key to Communicate with Machine", required=True),
	}
	_sql_constraints = [
		('unique_machine_id', 'unique(machine_id)', "Machine ID already defined on other machine, Machine ID must be Unique"),
	]

	def init_socket(self,cr,uid,ids,context={}):
		return socket.socket(socket.AF_INET,socket.SOCK_STREAM) #tcp socket

	# @return xml from xml.etree
	def _request_to_machine(self, cr, uid, machine_ip, headers, xml, context={}):
		req = urllib2.Request("http://"+machine_ip+"/iWsService",data=xml,headers=headers)
		res = urllib2.urlopen(req)
		response = res.read()
		return response

	def stream_data_http(self,cr,uid,ids,context={}):
		# print "aaaaaaaaaaaaaaaaaaaaaaaaaaaa"
		hr_employee = self.pool.get('hr.employee')

		machines = self.browse(cr,uid,ids,context=context)
		headers = {
			'Content-Type':'text/xml'
		}
		for mac in machines:
			xml = """<GetAttLog><ArgComKey xsi:type="xsd:integer">{machine_key}</ArgComKey>
			<Arg><PIN xsi:type="xsd:integer">All</PIN></Arg></GetAttLog>""".format(machine_key=mac.key)
			
			response = self._request_to_machine(cr, uid, mac.ip, headers, xml, context=context)

			log_tree = ET.fromstring(response)
			dictResponse = xmltodict.parse(response) # JSON Formatted Log from machine
			dictRowsResponse = dictResponse['GetAttLogResponse']['Row'] #[0]['PIN']
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
						<ArgComKey xsi:type="xsd:integer">78772</ArgComKey>
						{PINS}
					</GetUserInfo>""".format(PINS=xml_pin)
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
		
		return True



class hr_attendance_manual_reason(osv.osv):
	_name = 'hr.attendance.manual.reason'
	_columns = {
		'name': fields.char('Name',required=True),
		'desc': fields.text('Short Description',required=False),
	}


class hr_attendance_log(osv.osv):
	def _convert_date_to_epoch(self,str_datetime):
		res = False
		res = int(time.mktime(time.strptime(str_datetime, '%Y-%m-%d %H:%M:%S')))
		return res
	def create(self,cr,uid,vals, context={}):
		# IF MANUAL
		if 'manual_log_time' in vals:
			vals['datetime_log'] = self._convert_date_to_epoch(vals['manual_log_time'])
			print vals, '----------------------', context

		else:
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
		'state': fields.selection([('0','Draft'), ('1','Machine Validation'), ('2', 'Ask For Revision'), ('3', 'Done')], string="State"),
		'is_manual': fields.boolean(string="Is Manual Input"),
		'manual_reason_id': fields.many2one('hr.attendance.manual.reason',string="Reason"),
		'manual_log_time': fields.datetime('Manual Log Time',required=False),
		'notes': fields.text(string="Notes", required=False),
		'log_time': fields.function(_get_log_time_from_epoch, method=True, string="Log Time", store=True, type="datetime"),
		'machine_id': fields.many2one('hr.attendance.machine',string='Machine ID',required=True),
	}

	def check_is_log_exists(self,cr,uid,eid,datetime_log,context={}):

		res = self.search(cr,uid,[('att_pin','=',eid), ('datetime_log','=',datetime_log)], context=context)
		# print "searching ",eid," and ",datetime_log
		# print res,"---------->>RES"
		return res

class hr_attendance_min_max_log(osv.osv):
	_name = "hr.attendance.min.max.log"
	_description = "HR Attendance Min Max Log"
	_auto = False
	_columns = {
		'employee_id': fields.many2one('hr.employee',string="Employee"),
		'dept_id': fields.many2one('hr.department',string="HR Department"),
		'employee_name': fields.char('Employee Name'),
		'dept_name': fields.char('Department'),
		'y_log': fields.char('Year'),
		'm_log': fields.char('Month'),
		'd_log': fields.char('Day'),
		'min_log': fields.char('Min Scanned Time'),
		'min_state_log': fields.integer('Min Time Scanned State'),
		'max_log': fields.char('Max Scanned Time'),
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
				grouped3.y_log,
				grouped3.m_log,
				grouped3.d_log,
				grouped3.scan_times_a_day,
				grouped3.min_log,
				grouped3.min_state_log,
				(CASE WHEN grouped3.max_log = grouped3.min_log THEN '-' ELSE grouped3.max_log END) AS max_log,
				grouped3.max_state_log,
				to_char((EXTRACT(EPOCH FROM attendance_time) || ' second')::interval, 'HH24:MI:SS') as attendance_time
			FROM (
				SELECT
					grouped2.dept_id,
					grouped2.dept_name,
					grouped2.employee_id,
					grouped2.y_log,
					grouped2.m_log,
					grouped2.d_log,
					grouped2.employee_name,
					grouped2.scan_times_a_day,
					to_char(grouped2.min_log,'YYYY-MM-DD HH24:MI:SS') AS min_log,
					grouped2.min_state_log,
					to_char(grouped2.max_log,'YYYY-MM-DD HH24:MI:SS') AS max_log,
					grouped2.max_state_log,
					age(max_log,min_log) as attendance_time
					--age(max_log,min_log) - interval '1 hour' as attendance_time
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
							EXTRACT(DAY FROM att_log_dec.timestamp_log) AS d_log
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
					GROUP BY hdep.id, hdep.name, grouped1.employee_id, hem.name_related, grouped1.y_log, grouped1.m_log, d_log
					-- ORDER BY hdep.name, hem.name_related, grouped1.y_log, grouped1.m_log, d_log
					ORDER BY grouped1.y_log DESC, grouped1.m_log DESC, d_log DESC, hdep.name,hem.name_related,  min_log DESC
				) AS grouped2
			) AS grouped3
		)""")
hr_attendance_min_max_log()