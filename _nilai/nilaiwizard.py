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

class nilaiwizard(osv.osv_memory):
	_name ='wizard.nilai'
	_columns ={
		'matakuliah':fields.many2one('matakuliah','Nama matakuliah',required=True,ondelete='cascade',onupdate='cascade'),
		'nilai':fields.integer('Nilai'),
		'student_id':fields.many2one('student','Nama Murid',required=True,ondelete='cascade',onupdate='cascade')
	}

	""""
	@uid = (integer) id user
	@vals = (dictionary) value dari from
	@context = (dictionary) context
	"""
	def create(self,cr,uid,vals,context={}):
		print 'UID ==',uid
		print 'vals ==',vals
		print 'tesssssssssssstttasgd'
		print 'context ==',context
		if context.get('active_model',False) and context['active_model'] == 'student':
			vals['student_id'] = context['active_id']


		# print vals,"XXXXXXXXXXXXXXXXXXXXXXX"
		# raise osv.except_osv(_('Error'),_('EEERRRRROOOOOR'))
		return super(nilaiwizard,self).create(cr,uid,vals,context=context)


	def confirm(self,cr,uid,ids,context={}):
		print context,'context----'
		res = {}
		# # browse() untuk mining data dari database browse(cr,uid,ids,context) ids bisa list bisa integer
		datas = self.browse(cr, uid, ids[0], context=context)
		
		nilai_obj = self.pool.get('nilaiujian')
		# print nilai_obj.student_id

		vals = {
			'matakuliah': datas.matakuliah.id,
			'nilai':datas.nilai,
			'student_id': datas.student_id.id
		}

		return nilai_obj.create(cr,uid,vals,context=context)

		# raise osv.except_osv(_('Error'),_('EEERRRRROOOOOR'))

		# return res

