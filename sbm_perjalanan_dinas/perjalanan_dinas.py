import time
import netsvc
from osv import osv, fields

class Jenis_tunjangan(osv.osv):
	_name = 'jenis.tunjangan.expense'
	_columns = {
		'name':fields.char('Jenis Tunjangan',size=30),
	}

Jenis_tunjangan()

class Tunjangan(osv.osv):
	_name = 'tunjangan.expense'
	_columns = {
		'name':fields.char('Refference',required=True, readonly=True),
		'lokasi_dinas':fields.selection([(1,'Sumatera, Jawa , Bali , Bangka'),
			(2,'Kalimantan, Sulawesi, Kepulan Maluku'),
			(3,'NTB, NTT, Kepulan Timor'),(4,'Duri, Batam, Kepulan Riau'),
			(5,'Papua, Kepulan Papua'),
			(6,'Luar Negeri')],'Lokasi Dinas',required=True),
		'golongan' : fields.selection([('1','Golongan 1'),('2','Golongan 2'),('3','Golongan 3'),('4','Golongan 4'),('5','Golongan 5')],'Golongan',required=True),
        'status':fields.selection([('1','Tidak Menginap'),('2','Menginap')],'Status',required=True),
        'tunjangan_detail_dinas_ids': fields.one2many('detail.tunjangan.dinas', 'detail_tunjangan_dinas_id', 'Detail Tunjangan'),
	}

	_defaults = {'name': '/'}
	
	def create(self, cr, uid, vals, context=None):
		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tunjangan.dinas')
		return super(Tunjangan, self).create(cr, uid, vals, context=context)
	
Tunjangan()

class Detail_Tunjangan_Dinas(osv.osv):
    _name = 'detail.tunjangan.dinas'
    _columns = {
        'name':fields.many2one('jenis.tunjangan.expense','Jenis Tunjangan'),
        'jumlah_tunjangan':fields.integer('Jumlah Tunjangan', required=True),
        'detail_tunjangan_dinas_id':fields.many2one('tunjangan.expense', 'Detail Tunjangan', required=True, ondelete='cascade')
    }

Detail_Tunjangan_Dinas()

class Detail_expenses_dinas(osv.osv):
    _name ='hr.expense.dinas'
    _columns = {
    	'name':fields.char('Refference',readonly=True, states={'draft':[('readonly',False)]}),
    	'no_spk':fields.char('No SPK',readonly=True, states={'draft':[('readonly',False)]}),
    	'employee_id': fields.many2one('hr.employee', "Employee", required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'department_id':fields.many2one('hr.department','Department', readonly=True, states={'draft':[('readonly',False)]}),
        'golongan' : fields.selection([('1','Golongan 1'),('2','Golongan 2'),('3','Golongan 3'),('4','Golongan 4'),('5','Golongan 5')],'Golongan',readonly=True, states={'draft':[('readonly',False)]}),
        'lama_perjalanan':fields.integer('Lama Perjalanan (Hari)',size=2,readonly=True, states={'draft':[('readonly',False)]}),
        'lokasi_dinas':fields.selection([('1','Sumatera, Jawa , Bali , Bangka'),
    		('2','Kalimantan, Sulawesi, Kepulan Maluku'),
    		('3','NTB, NTT, Kepulan Timor'),('4','Duri, Batam, Kepulan Riau'),
    		('5','Papua, Kepulan Papua'),
    		('6','Luar Negeri')],'Lokasi Dinas',required=True,readonly=True, states={'draft':[('readonly',False)]}),
    	'tanggal_keberangkatan':fields.date('Tanggal Keberangkatan',required=True,readonly=True, states={'draft':[('readonly',False)]}),
    	'tanggal_kepulangan':fields.date('Tanggal Kepulangan',required=True,readonly=True, states={'draft':[('readonly',False)]}),
    	'maksud_perjalanan_dinas':fields.char('Tujuan Perjalanan Dinas',size=200,required=True, readonly=True, states={'draft':[('readonly',False)]}),
    	'customer_id':fields.many2one('res.partner','Customer',readonly=True, states={'draft':[('readonly',False)]}),
    	'status':fields.selection([('1','Tidak Menginap'),('2','Menginap')],'Status',required=True,states={'confirm':[('readonly',True)],'done':[('readonly',True)],'ticketing':[('readonly',True)]}),
        'dibebankan':fields.char('Akan Di Bebankan',readonly=True, states={'draft':[('readonly',False)]}),
    	'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('ticketing','Ticketing'),
            ('done', 'Done'),
            ],
            'Status'),
        'real_lokasi':fields.char('Real Lokasi',states={'draft':[('readonly',True)]}),
    	'tunjangan_transport_ids': fields.one2many('tunjangan.transport', 'tunjangan_transport_id', 'Transport',readonly=True, states={'draft':[('readonly',True)],'ticketing':[('readonly',False)]}),
    	'tunjangan_meal_hotel_ids': fields.one2many('tunjangan.meal.hotel', 'tunjangan_meal_hotel_id', 'Meal dan Hotel',readonly=True, states={'draft':[('readonly',False)],'ticketing':[('readonly',True)]}),
    }
    def _employee_get(obj, cr, uid, context=None):
	    if context is None:
	        context = {}
	    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
	    if ids:
	        return ids[0]
	    return False

    def _golongan_get(obj, cr, uid, context=None):
	    if context is None:
	        context = {}
	    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
	    if ids:
	        golid = obj.pool.get('hr.employee').browse(cr, uid, ids[0]).golongan
	        return golid
	    return False

    def _department_get(obj, cr, uid, context=None):
	    if context is None:
	        context = {}
	    ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
	    if ids:
	        depds = obj.pool.get('hr.employee').browse(cr, uid, ids[0]).department_id.id
	        return depds
	    return False

    def submit(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{'state':'confirm'})

    def confirm(self,cr,uid,ids,context=None):
        val = self.browse(cr, uid, ids)[0]
        usermencet = self.pool.get('res.user')
        #print 'manager ===================>', val.employee_id.parent_id.id
        #print 'user mencet ##################>', uid 
        if val.employee_id.parent_id.id != uid :
            raise osv.except_osv(('Perhatian..!!'), ('Harus Atasannya langsung ..'))
        return self.write(cr,uid,ids,{'state':'ticketing'})

    def setdraft(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{'state':'draft'})

    def submitticketing(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{'state':'done'})

    _defaults = {
    	'name':'/',
        'state': 'draft',
        'employee_id': _employee_get,
        'department_id' : _department_get,
        'golongan' : _golongan_get,
        'lama_perjalanan':1,
    }

    def create(self, cr, uid, vals, context=None):
		vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.expense.dinas')
		return super(Detail_expenses_dinas, self).create(cr, uid, vals, context=context)

    def hitung_tunjangan(self,cr,uid,ids,idLJ,idEP,idLP,ST):
    	if idLP:
			id_employee = self.pool.get('hr.employee').browse(cr,uid,idEP) 
				
			golongan = id_employee.golongan
			cek=self.pool.get('tunjangan.expense').search(cr,uid,[('golongan', '=' ,golongan),('lokasi_dinas', '=' ,idLJ),('status', '=', ST)])
			if cek:
				data = []
				hasil=self.pool.get('tunjangan.expense').browse(cr,uid,cek)[0]
				for x in hasil.tunjangan_detail_dinas_ids :
					data.append({
						'name': x.name.name,
						'harga': x.jumlah_tunjangan,
						'qty':idLP,
						'subtotal':x.jumlah_tunjangan*idLP,
						})
				return {'value':{ 'tunjangan_meal_hotel_ids':data} }
			return True

    def reportexspense(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'hr.expense.dinas'
        datas['form'] = self.read(cr, uid, ids)[0]
 
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr.expense.dinas',
            'report_type': 'webkit',
            'datas': datas,
        }

        
Detail_expenses_dinas()


class Tunjangan_transport(osv.osv):
    _name = 'tunjangan.transport'
    
    _columns = {
        'name':fields.selection([('1','Darat'),
    		('2','Laut'),
    		('3','Udara')],'Jenis Transport', required=True),
        'tgl':fields.datetime('Tanggal Keberangkatan',required=True),
        'refference':fields.char('Refference',required=True),
        'harga':fields.integer('Unit Price',required=True),
        'qty':fields.integer('Quantities',required=True),
        'subtotal':fields.integer('Sub Total'),
        'tunjangan_transport_id':fields.many2one('hr.expense.dinas', 'Tunjangan Transport', required=True, ondelete='cascade')
    }

    def hitung_subtotal(self,cr,uid,ids,qty,harga):
		subtotal=qty*harga
		return {'value':{ 'subtotal':subtotal } }


Tunjangan_transport()


class Tunjangan_meal_hotel(osv.osv):
    _name = 'tunjangan.meal.hotel'
    
    _columns = {
        'name':fields.char('Jenis Tunjangan', required=True),
        'refference':fields.char('Refference'),
        'harga':fields.integer('Unit Price',required=True),
        'qty':fields.integer('Quantities',required=True),
        'subtotal':fields.integer('Sub Total'),
        'tunjangan_meal_hotel_id':fields.many2one('hr.expense.dinas', 'Tunjangan Meal Hotel', required=True, ondelete='cascade')
    }

Tunjangan_meal_hotel()



