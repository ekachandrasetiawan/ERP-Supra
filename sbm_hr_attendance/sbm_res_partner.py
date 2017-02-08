import time
from datetime import date, timedelta, datetime
import netsvc
from tools.translate import _
from osv import osv, fields

class res_partner(osv.osv):

	_inherit = "res.partner"
	_columns = {
		'is_site':fields.boolean(string='Is Site'),
	}

	_default = {
		'is_site': False,
	}
	
res_partner()