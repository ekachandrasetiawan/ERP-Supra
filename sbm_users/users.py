import time
from openerp import netsvc
from datetime import date, timedelta, datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.exceptions


class Public_Ip_Address(osv.osv):
	
	_name = "public.ip.address"

	def redirect(self, cr, uid, ids, context=None):
		m  = self.pool.get('ir.model.data')
		id_group = m.get_object(cr, uid, 'sbm_users', 'group_using_public_ip_address').id
		user_group = self.pool.get('res.groups').browse(cr, uid, id_group)

		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)


		if user_group:
			for x in user_group.users:
				if uid == x.id:
					# Ip Public
					searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print.public')], context=context)

		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
		
		res = str(browseConf.value)

		return res

Public_Ip_Address()