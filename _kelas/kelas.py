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

class kelas(osv.osv):
	_name = 'kelas'
	_description = 'kelas'
	# _rec_name = 'kelasmana'
	_columns = {
		'name':fields.char('Nama Kelas',required=True),
		'student_ids':fields.one2many('student','kelasmana','kelas')
		}

class student(osv.osv):	
	_inherit ='student'
	_columns = {
		'kelasmana':fields.many2one('kelas',string='kelas')		
	}
	
