from datetime import datetime
from stock import stock
import math
import time
import webbrowser
import netsvc
from datetime import datetime
import openerp.exceptions
from osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import re
class product_product(osv.osv):
	_inherit = 'product.product'

	def code_change(self,cr,uid,ids,default_code):
		res = super(product_product,self).code_change(cr,uid,ids,code=default_code)

		print res
		# pattern = re.compile("[^a-zA-Z0-9]")
		print re.sub(r'[^a-zA-Z0-9]','',res["value"]["default_code"])
		onchange_default = re.sub(r'[^a-zA-Z0-9]','',res["value"]["default_code"])
		res['value']["default_code"] = onchange_default
		# matchObj =pattern.search(res["value"]["default_code"])	
		# if matchObj:
		# 	print "selain number dan karakter"
		# else:
		# 	print "hanya number dan karakter okkk"

		return res
