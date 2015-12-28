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

class nilai(osv.osv):
	_name = 'nilaiujian'
	_description ='nilai'
	_columns = {
		'matakuliah':fields.many2one('matakuliah','Nama matakuliah',required=True,ondelete='cascade',onupdate='cascade'),
		'nilai':fields.integer('Nilai'),
		'student_id':fields.many2one('student','Nama Murid',required=True,ondelete='cascade',onupdate='cascade')
	}

class student(osv.osv):
	_inherit = 'student'
	_columns = {
		'nilai_ids': fields.one2many('nilaiujian','student_id',string="Nilai"),
	}