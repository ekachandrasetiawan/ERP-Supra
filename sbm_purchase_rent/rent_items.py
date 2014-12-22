import time
import netsvc
from osv import osv, fields
import re
import csv
import base64
import calendar
import datetime
from osv import fields, osv
import decimal_precision as dp


# Model Rent Requisition
class RentItems (osv.osv):
	# _name = 'rent.items'
	_inherit = 'product.product'
	_columns = {
		'is_rent_item': fields.boolean('Is Rent Item'),
		'not_stock': fields.boolean('Not Stock')
	}

	def turnover(self,cr,uid,ids,context=None):
		searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
		browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]

		val = self.browse(cr, uid, ids)[0]
		idproduct=str(val.id)
		print '=====================================',idproduct
		urlTo = str(browseConf.value)+"report-accounting/turn-over&id="+idproduct

		return {
            'type'  : 'ir.actions.client',
            'target': 'new',
            'tag'   : 'print.out.turnover',
            'params': {
                # 'id'  : ids[0],
                'redir' : urlTo,
                'uid':uid
            },
        }


RentItems()