import netsvc
from osv import osv, fields

class Permission(osv.osv):
	_name = 'permission.employee'
	_columns = {
		'name':fields.char('Refference',required=True, readonly=True),
		'employee_id':fields.many2one('hr.employee','Nama Karyawan',required=True),
		'dept_id':fields.many2one('hr.department','Dept/Bagian',required=True),
		'keperluan':fields.selection([('perusahaan','Perusahaan'),('pribadi','Pribadi')],'Keperluan',required=True),
		'tanggal_jam_keluar':fields.datetime('Tanggal Jam Keluar'),
		'tanggal_jam_masuk':fields.datetime('Tanggal Jam Masuk'),
		'kembali':fields.selection([('ya','Ya'),('tidak','Tidak')],'Kembali Ke Kantor',required=True),
		'security':fields.char('Petugas Security',size=30)
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

	_defaults = {
    	'name':'/',
        'employee_id': _employee_get,
        'dept_id' : _department_get,
    }
	
	def create(self, cr, uid, vals, context=None):
		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'permission.employee')
		return super(Permission, self).create(cr, uid, vals, context=context)

Permission()

class PermissionWizard(osv.osv_memory):
    _name = "permission.wizard"
    _columns = {
    			'name': fields.char('File Name', 16),
    			'date_from':fields.date('Date From'),
    			'date_to':fields.date('Date To'),
           		'user_ids' : fields.many2many('res.users','wizard_user_rel','user_id','wizard_id','Employee',required=True)
    }   

    def print_permission_report																																																		(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        print "----------",context
        x = {'ids':context.get('active_ids',[])}
        x['model'] = 'salesprospectrecord.crm'
        x['form'] = self.read(cr,uid,ids)[0]
        diction = {
            'type': 'ir.actions.report.xml',
            'report_name': 'salesprospectrecord.crm.form.xls',
            'report_type': 'webkit',
            'datas': x,
        }
        #print "=-===",diction
        return diction
 
PermissionWizard()