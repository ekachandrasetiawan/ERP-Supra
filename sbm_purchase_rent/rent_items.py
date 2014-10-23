import time
import netsvc
from osv import osv, fields


# Model Rent Requisition
class RentItems (osv.osv):
	# _name = 'rent.items'
	_inherit = 'product.product'
	_columns = {
		'is_rent_item': fields.boolean('Is Rent Item'),
		'not_stock': fields.boolean('Not Stock')
	}
RentItems()