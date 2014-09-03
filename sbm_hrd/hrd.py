import time
import netsvc
from osv import osv, fields

class Siteemployee(osv.osv):
    _name = 'hrd.siteemployee'
    _culumns = {
                'sitaktual': fields.char('Site Aktual', 128, required=True), 
                }
Siteemployee()

class Detailhrd(osv.osv):
    _inherit ='hr.employee'
    _columns = {
                'nik':fields.char('NIK'),
                'ktp':fields.char('Nomor KTP'),
                'level':fields.char('Level'),
                'alamat_tinggal':fields.char('Residence Address'),
                'alamat_ktp':fields.char('KTP Address'),
                'job_id': fields.many2one('hr.job', 'Jabatan (Diajakuan)'),
                'jabatan':fields.many2one('hr.job','Jabatan'),
                'siteawal_id': fields.many2one('site','Site Awal'),
                'siteaktual':fields.many2one('site','Site Aktual'), 
                'tglmasuk': fields.date('Tanggal Masuk'),
                'golongan_darah':fields.char('Golongan Darah'),
                'golongan' : fields.selection([('1','Golongan 1'),('2','Golongan 2'),('3','Golongan 3'),('4','Golongan 4'),('5','Golongan 5')],'Golongan'),
                'surat_tunjangan_ids': fields.one2many('surat.tugas', 'surat_tunjangan_id', 'Surat Tugas'),
                'riwayat_penyakit_ids':fields.one2many('riwayat.penyakit','riwayat_penyakit_id','Riwayat Penyakit'),        
                'medical_record_ids':fields.one2many('medical.record','medical_record_id','Riwayat Penyakit'),
                }

Detailhrd()

class SuratTugas(osv.osv):
    _name    = 'surat.tugas'
    _columns = {
                'name':fields.char('Surat Tugas'),
                'surat_tunjangan_id':fields.many2one('hr.employee', 'Employee', ondelete='cascade')
            }
SuratTugas()

class RiawayatPenyakit(osv.osv):
    _name = 'riwayat.penyakit'
    _columns = {
                'name':fields.char('Riwayat Pemyakit'),
                'riwayat_penyakit_id':fields.many2one('hr.employee', 'Employee', ondelete='cascade')
    }

RiawayatPenyakit()

class MedicalRecord(osv.osv):
    _name = 'medical.record'
    _columns = {
                'name':fields.char('Refference',readonly=True),
                'medical_check_up':fields.char('Medical Check Up'),
                'claims':fields.integer('Claims Rawat Jalan / Rawat Inap'),
                'medical_record_id':fields.many2one('hr.employee', 'Employee', ondelete='cascade')
    }

    _defaults = {
        'name':'/'
    }

MedicalRecord()

class site(osv.osv):
	_name = 'site'
	_columns = {
			'name':fields.char('Site',size=128, required=True),
    }
site()

class jabatan(osv.osv):
    _name = 'jabatan'
    _columns = {
            'name':fields.char('Jabatan',size=128),
    }