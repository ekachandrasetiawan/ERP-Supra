import time
import netsvc
from osv import osv, fields


# Model Rent Requisition
class TermOfPayment (osv.osv):
	_inherit = 'res.partner'
	_columns = {
		'term_payment': fields.text('Term Of Payment')
	}
TermOfPayment()


class TermOfPaymentPO(osv.osv):
	_inherit = 'purchase.order'
	_columns = {
		'term_of_payment' : fields.text('Term Of Payment',required=False)
	}
TermOfPaymentPO()