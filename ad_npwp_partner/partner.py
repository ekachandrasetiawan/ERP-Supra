from osv import osv, fields
from tools.translate import _

class partner(osv.osv):
	_inherit = 'res.partner'
	_columns = {'npwp' : fields.char('No. NPWP', size=20, required=False, help='Misal 01.540.674.7.431-000'),}

	def onchange_format_npwp(self, cr, uid, ids, npwp):
		if npwp:
			if npwp=='11111111111111111111':
				return {'value': {'npwp': '11111111111111111111'}}
			else:
				result = ''
				warning = {"title": ("NPWP Number Format Incorrect!"), "message": ("Masukan 15 digit NPWP tanpa tanda baca")}
				if len(npwp) != 15 :
					return {'warning': warning, 'value': {'npwp': result}}
				elif not npwp.isdigit():
					return {'warning': warning, 'value': {'npwp': result}}
				else:
					result = npwp[:2] + '.' + npwp[2:5] + '.' + npwp[5:8] + '.' + npwp[8] + '-' + npwp[9:12] + '.' + npwp[-3:] 
					return {'value': {'npwp': result}}
		return True

	def create(self, cr, uid, vals, context=None):
		if 'parent_id' in vals:
			return super(partner, self).create(cr, uid, vals, context=context)
		else:
			if vals['is_company']==True:
				if vals['npwp']=='11111111111111111111':
					vals['npwp']=='11111111111111111111'
				else:
					cek=self.pool.get('res.partner').search(cr,uid,[('npwp', '=' ,vals['npwp'])])
					if cek:
						raise osv.except_osv(('Perhatian..!!'), ('No NPWP Unique ..'))
		return super(partner, self).create(cr, uid, vals, context=context)

	def write(self,cr,uid,ids,vals,context={}):
		cek=self.pool.get('res.partner').search(cr,uid,[('id', '=' ,ids)])
		hasil=self.pool.get('res.partner').browse(cr,uid,cek)[0]
		
		if hasil['is_company']==True:
			# NPWP di awal tidak ada, maka hasilnya False
			if hasil['npwp']==False:
				if vals['npwp']=='11111111111111111111':
					vals['npwp']=='11111111111111111111'
				else:
					cek=self.pool.get('res.partner').search(cr,uid,[('npwp', '=' ,vals['npwp'])])	
					if cek:
						raise osv.except_osv(('Perhatian..!!'), ('No NPWP Unique ..'))
			
			# NPWP awal ada valuenya
			else:
				if 'npwp' in vals:
					if vals['npwp']=='11111111111111111111':
						vals['npwp']=='11111111111111111111'
					else:
						cek=self.pool.get('res.partner').search(cr,uid,[('npwp', '=' ,vals['npwp'])])
						if cek:
							raise osv.except_osv(('Perhatian..!!'), ('No NPWP Unique ..'))
							
		return super(partner, self).write(cr, uid, ids, vals, context=context)

partner()


class AccountInvoice(osv.osv):
	_inherit = "account.invoice"
	_columns = {
			'kmk': fields.char('KMK', size=64, select=True),
			'kurs': fields.float('Kurs BI', digits=(12,2), select=True),
			'pajak': fields.float('Kurs Pajak', digits=(12,2), select=True),
			'kwitansi': fields.char('Kwitansi', size=64, select=True),
			'faktur_pajak_no' : fields.char('Faktur Pajak', size=20, required=False, help='Misal 010.000-10.00000001'),
	}
	
	def onchange_format_faktur(self, cr, uid, ids, no):
		try:
			int(no)
			if len(no) == 16:
				value = list(no)
				value.insert(3, '.')
				value.insert(7, '-')
				value.insert(10, '.')
				result = "".join(value)
				return {'value': {'faktur_pajak_no': result}}      
			else:
				return {'warning': {"title": _("Perhatian"), "message": _("Nomor faktur pajak harus 16 digit")}, 'value': {'faktur_pajak_no': False}}
		except:
			return {'warning': {"title": _("Perhatian"), "message": _("Masukan 16 digit angka tanpa separator")}, 'value': {'faktur_pajak_no': False}}
		
		
AccountInvoice()

