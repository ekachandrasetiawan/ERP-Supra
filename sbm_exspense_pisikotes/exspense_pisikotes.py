import netsvc
from osv import osv, fields

class Peserta_Pisikotes(osv.osv):
	_name = 'peserta.pisikotes'
	_columns = {
		'name' :fields.char('name'),
		'nama_peserta':fields.char('Nama Peserta'),
		'department_id':fields.many2one('hr.department','Department'),
		'peserta_pisikotes_id':fields.many2one('exspense.pisikotes', required=True, ondelete='cascade')
	}

Peserta_Pisikotes()

class exspense_pisikotes(osv.osv):
	_name = 'exspense.pisikotes'
	_columns = {
		'name' : fields.char('name'),
		'no_invoice':fields.char('No Invoice',size=20,required=True),
		'tgl_awal_tes':fields.date('Tanggal Awal'),
		'tgl_akhir_tes':fields.date('Tanggal Akhir'),
		'harga_pisikotes':fields.float('Harga Pisikotes (Perorang)', digits=(16,2)),
		'jumlah_peserta': fields.integer('Jumlah Peserta'),
		'total_harga':fields.float('Total Harga', digits=(16,2)),
		'ppn':fields.float('PPN 10%', digits=(16,2)),
		'total_bayar':fields.float('Total Bayar', digits=(16,2)),
		'peserta_pisikotes_ids': fields.one2many('peserta.pisikotes', 'peserta_pisikotes_id'),
	}

	_defaults = {'harga_pisikotes':350000}

	def proses(self,cr,uid,ids,Tharga,Tpeserta):
		if (Tpeserta):
			Thrg=Tharga*Tpeserta;
			ppn=Thrg*0.1;
			bayar=Thrg+ppn;
			return {'value':{ 'total_harga':Thrg, 'ppn':ppn, 'total_bayar':bayar} }
			return True

exspense_pisikotes()