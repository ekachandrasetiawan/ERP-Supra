import openerp.exceptions
import os, subprocess
import json
import socket
import httplib, urllib
import telnetlib
import requests
from osv import osv, fields


class hr_carrier_level(osv.osv):
	_name = 'hr.carrier.level'
	_columns = {
		'name' : fields.char("Name", help="Short Description For Carrier Code Or Name",required=True,size=10),
		'description': fields.text("Description",required=False),
		'active': fields.boolean('Active',required=False),
		'employees': fields.one2many('hr.employee','carrier_level_id',string="Employees", onupdate="CASCADE", ondelete="RESTRICT"),
	}

	_sql_constraint = {
		('hr_carrier_level_name_unique','unique(name)','Name is already Exist, Cant create new one with exist name because name must be unique')
	}

class hr_employee_religion(osv.osv):
	_name = 'hr.employee.religion'
	_columns = {
		'name': fields.char('name',required=True,size=30),
		'employees': fields.one2many('hr.employee','religion_id',string="Employees", onupdate="CASCADE", ondelete="RESTRICT"),
	}

class hr_employee(osv.osv):
	_inherit = 'hr.employee'
	_columns = {
		'employee_code': fields.char("Employee Code",required=False,size=20),
		'carrier_level_id': fields.many2one('hr.carrier.level',string="Carrier Level", onupdate="CASCADE", ondelete="RESTRICT",required=False),
		'religion_id': fields.many2one('hr.employee.religion',string="Religion",required=False, onupdate="CASCADE", ondelete="RESTRICT"),
		'blood_type': fields.selection([('A',"A"),('B','B'),('O','O'), ('AB','AB')],string="Blood Type"),
		'birth_place': fields.char('Birth Place', required=False, size=100),
		# 'last_edu_degree_id': fields.many2one('hr.recruitment.degree',required=False,string="Last Education Degree", onupdate="CASCADE", ondelete="RESTRICT"),
		'home_phone' : fields.char('Home Phn', required=False),
		'private_mobile_no': fields.char('Private Mobile Phn No.'),
		# 'identity_identity_no' : fields.char('Identity Card No',required=True,size=20),
		'identity_attachment_ids': fields.many2many('ir.attachment', 'hr_employee_identity_attachment_rel', 'employee_id', 'attachment_id', 'Identity Attachments'),
		'identity_card_expire_date': fields.date('Identity Card Valid Until',required=False),
		'identity_card_image': fields.binary(string="ID Card Image File", required=False),
		'employment_status': fields.selection([('permanent','Permanent'),('contract','Contract'), ('outsource','Outsource')],required=False, string="Employment Status"),
	}
	# _defaults = {
	# 	'religion_id':1
	# }
	def action_test(self, cr, uid, ids, context=None):
		
		content = """<GetAttLog>
		<ArgComKey xsi:type="xsd:integer">78772</ArgComKey>
		<Arg><PIN xsi:type="xsd:integer">All</PIN></Arg></GetAttLog>"""
		header = "POST /iWsService HTTP/1.0\r\nContent-Type: text/xml\r\nContent-Length: "+str(len(content))+"\r\n\r\n"
		# print body
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #tcp socket
		
		s.connect(('10.36.14.229', 80))
		
		# s.send("POST /iWsService HTTP/1.0\r\n")
		# s.send("Content-Type: text/xml\r\n")
		# s.send("Content-Length: "+str(len(content))+"\r\n\r\n")
		
		# s.send(content)

		body = header+content
		s.send(body)		
		datas = []
		loop = 1
		while loop:
			try:
				data = s.recv(4096)
				if data:
					datas.append(data)
				else:
					loop=0
			except s.error:
				print "Socket Error"
				loop = 0
				pass
		print datas, 'aaaaaaaaaaaaaaa'
		s.close()
