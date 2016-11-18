import time
from openerp import netsvc
from datetime import date, timedelta, datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.exceptions


class purchase_order_warehouse(osv.osv):
    _name = "purchase.order.warehouse"
    _inherit = "purchase.order"
    _table = "purchase_order"
    _description = "Purchase Order"

	
purchase_order_warehouse()