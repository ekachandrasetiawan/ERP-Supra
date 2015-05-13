import time
from datetime import date, timedelta, datetime
import netsvc
from osv import osv, fields

class HRpermission(osv.osv):
	_name = 'hr.permission.employee'
	_columns = {
		'name':fields.char('Refference',required=True, readonly=True),
		'employee_id':fields.many2one('hr.employee','Nama Karyawan',required=True),
		'dept_id':fields.many2one('hr.department','Dept/Bagian',required=True),
		'keperluan':fields.selection([('perusahaan','Perusahaan'),('pribadi','Pribadi')],'Keperluan',required=True),
		'tujuan':fields.text('Tujuan'),
		'tanggal_jam_keluar':fields.datetime('Tanggal Jam Keluar'),
		'tanggal_jam_masuk':fields.datetime('Tanggal Jam Masuk'),
		'kembali':fields.selection([('ya','Ya'),('tidak','Tidak')],'Kembali Ke Kantor',required=True),
		'security':fields.char('Petugas Security',size=30),
    	'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Check Manager'),
            ('confirm2', 'Check HRD'),
            ('done', 'Done'),
            ],
            'Status'),
	}

	def _employee_get(obj, cr, uid, context=None):
	    if context is None:
	        context = {}
	    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
	    if ids:
	        return ids[0]
	    return False

	def _department_get(obj, cr, uid, context=None):
	    if context is None:
	        context = {}
	    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
	    if ids:
	        depds = obj.pool.get('hr.employee').browse(cr, uid, ids[0]).department_id.id
	        return depds
	    return False

	def dept_change(self,cr,uid,ids,pid):
		employee_id = self.pool.get('hr.employee').browse(cr,uid,pid) 
		dept_id = employee_id.department_id.id
		return {'value':{ 'dept_id':dept_id} }

	def create(self, cr, uid, vals, context=None):
		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.permission.employee')
		return super(HRpermission, self).create(cr, uid, vals, context=context)

	def submit(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'confirm'})

	def approve(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids)[0]
		usermencet = self.pool.get('res.user')
		if val.employee_id.parent_id.id != uid :
			raise osv.except_osv(('Perhatian..!!'), ('Harus Atasannya langsung ..'))
		return self.write(cr,uid,ids,{'state':'confirm2'})

	def validate(self,cr,uid,ids,context=None):
		val = self.browse(cr, uid, ids)[0]
		usermencet = self.pool.get('res.user')
		if val.employee_id.department_id.name != 'HRD' :
			raise osv.except_osv(('Perhatian..!!'), ('Harus Dept HRD langsung ..'))

		return self.write(cr,uid,ids,{'state':'done'})

	def setdraft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':'draft'})

	_defaults = {
		'name': '/',
		'tanggal_jam_keluar':time.strftime('%Y-%m-%d'),
		'tanggal_jam_masuk':time.strftime('%Y-%m-%d'),
        'employee_id': _employee_get,
        'dept_id' : _department_get,
        'state': 'draft',
    }

HRpermission()