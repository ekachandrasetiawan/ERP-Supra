from datetime import datetime
import netsvc
from osv import osv, fields


class POContract(osv.osv):
	_inherit = 'purchase.order'
	_columns = {
		'contract_id' : fields.many2one('purchase.order.contract.data','Contract',ondelete="Cascade"),
		'contract_no' : fields.related('contract_id','contract_no',type="char",string="Contract No",store=False),
		'start_contract' : fields.related('contract_id','start_contract',type="date",string="Contract Start",store=False),
		'expire_contract' : fields.related('contract_id','expire_contract',type="date",string="Contract Expire",store=False),
		'notes' : fields.related('contract_id','notes',type="text",string="Notes",store=False),
	}

	# def write(self,cr,uid,ids,vals,context=None):
	# 	return False
		
POContract()


class POContractData(osv.osv):
	_name = 'purchase.order.contract.data'
	_rec_name = 'contract_no'
	_columns = {
		'contract_no' : fields.char('Contract No',30,required=True),
		'start_contract' : fields.date('Date Start',required=True),
		'expire_contract' : fields.date('Expire Contract',required=True),
		'notes'	: fields.text('Notes'),
		'pos'	: fields.one2many('purchase.order','contract_id','POs')
	}
POContractData()