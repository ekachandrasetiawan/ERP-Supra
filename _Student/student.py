from datetime import datetime
from stock import stock
import math
import time
import webbrowser
import netsvc
import openerp.exceptions
from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class student(osv.osv):
	_name = 'student'
	_description = 'student'
	_inherit = ['mail.thread']
	_columns = {
		'name':fields.char('Nama',required=True,track_visibility="onchange"),
		'umur':fields.date('Tanggal Lahir',track_visibility="onchange"),
		'alamat':fields.char('Alamat',track_visibility="onchange"),
		'state':fields.selection([('draft','Draft'),('approve','Approved'),('done','Done'),('cancel','Canceled')],string="State",track_visibility="always")
		
	}
	_defaults={
		
		'state':'draft'
	}


	# DEF WRITE SESUAI FLOW CHART
	"""
	def write(self,cr, uid, ids, values, context=None):
		# override
		# menggantikan funghsi asli
		print ids,'IDSSSSSSSSSS>>>>>'
		print values,'<<<<<<<<<<<<<<<<<<<<<<<Values'
		print context,'<<<<<<<<<<<<<<<<<<<<<<<Context'


		state_baru = values['state']


		data_sekarang = self.browse(cr,uid,ids,context=context)[0]
		# print data_sekarang

		if values['state']=='approve':
			if data_sekarang.state=='draft':
				return super(student,self).write(cr,uid,ids,values,context=context)
			else:
				return False

		elif values['state']=='done':
			if data_sekarang.state=='approve':
				return super(student,self).write(cr,uid,ids,values,context=context)
			else:
				return False
		elif values['state']=='cancel':
			if data_sekarang.state=='approve' or data_sekarang.state=='draft':
				return super(student,self).write(cr,uid,ids,values,context=context)
			else:
				return False
		elif values['state']=='draft':
			if data_sekarang.state=='approve':
				return super(student,self).write(cr,uid,ids,values,context=context)
			else:
				return False
		else:
			return False

	"""
	# def write pengembangan
	def write(self,cr, uid, ids, values, context=None):
		
		isAllow = False
		data_sekarang = self.browse(cr,uid,ids,context=context)[0]
		print data_sekarang.state

		if values.get('state'):
			 #variable untuk tanda apa boleh di update atau tidak
			state_baru = values['state']
			

			if values['state']=='approve':
				if data_sekarang.state=='draft':
					if values.get('name') or values.get('umur') or values.get('alamat') or values.get('kelasmana'):
						values['state'] = 'draft'
						
						return super(student,self).write(cr,uid,ids,values,context=context)
					else:
						# print 'gagal masuk'
						isAllow = True					
			# else:
			# 	isAllow	= False
			elif data_sekarang.state == 'draft':
				isAllow	= True
			elif data_sekarang.state == 'approve':
				if values.get('name') or values.get('umur') or values.get('alamat') or values.get('kelasmana'):
					values['state'] = 'draft'
						
					return super(student,self).write(cr,uid,ids,values,context=context)
				else:
						# print 'gagal masuk'
					isAllow = True	
			elif values['state']=='done':
				if data_sekarang.state=='approve':
					isAllow = True
				# else:
				# 	isAllow = False
			elif values['state']=='cancel':
				if data_sekarang.state=='approve' or data_sekarang.state=='draft':
					isAllow = True
				# else:
				# 	isAllow = False
			elif values['state']=='draft':
				if data_sekarang.state=='approve':
					isAllow = True
				# else:
				# 	isAllow = False
			elif values['state']=='draft':
				if data_sekarang.state=='draft':
					isAllow = True
				# else:
				# 	isAllow = False
			else:
				isAllow = False

			if isAllow:
				
				return super(student,self).write(cr,uid,ids,values,context=context)
			else:
				return False
		elif data_sekarang.state == 'approve':
				if values.get('name') or values.get('umur') or values.get('alamat') or values.get('kelasmana'):
					values['state'] = 'draft'
						
					return super(student,self).write(cr,uid,ids,values,context=context)			
		else:
			return super(student,self).write(cr,uid,ids,values,context=context)