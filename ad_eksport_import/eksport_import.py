import csv
import time
import base64
import tempfile
import datetime
import StringIO
import cStringIO
from dateutil import parser
from osv import fields, osv
from tools.translate import _


class EksportImport(osv.osv_memory):
    _name = "eksport.import"
    _columns = {
                'type': fields.selection((('eks','Export'), ('imp','Import')), 'Type'),
                'name': fields.char('File Name', 16),
                'tabel' : fields.many2one('ir.model', 'Object Model', required=True),
                'data_file': fields.binary('File'),
                }   
    _defaults = {'type' :'eks'}
    
    
    def eksport_excel(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        
        idd = self.pool.get(val.tabel.model).search(cr, uid, [])
        data = self.pool.get(val.tabel.model).read(cr, uid, idd)
      
        result = ';'.join(data[0].keys())   
        value = [d.values() for d in data]
        
        for v in value:
            for x in v:
                if isinstance(x, tuple):
                    v[v.index(x)] = x[0]
        
        for row in value:
            result += '\n' + ';'.join([str(v) for v in row]) 
            
        out = base64.encodestring(result)
        self.write(cr, uid, ids, {'data_file':out, 'name': 'eksport.csv'}, context=context)
        
        view_rec = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ad_eksport_import', 'view_wizard_eksport_import')
        view_id = view_rec[1] or False
    
        return {
            'view_type': 'form',
            'view_id' : [view_id],
            'view_mode': 'form',
            'res_id': val.id,
            'res_model': 'eksport.import',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
             
    def import_excel(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        if not val.data_file:
            raise osv.except_osv(_('Error'), _("Silahkan memilih file yang akan diimport !"))
        
        filename = val.name
        filedata = base64.b64decode(val.data_file)
        input = cStringIO.StringIO(filedata)
        input.seek(0)

        (fileno, fp_name) = tempfile.mkstemp('.csv', 'openerp_')
        file = open(fp_name, "w")
        file.write(filedata)
        file.close()
        
        crd = csv.reader(open(fp_name,"rb"))
        head = crd.next()[0].split(';')
        
        for row in crd:
            res = {}
            for x in range (0, len(row[0].split(';'))):
                r = row[0].split(';')[x]
                if r.upper() == 'FALSE':
                    r = False
                elif r.upper() == 'TRUE':
                    r = True
                else:
                    try:
                        r = float(r)
                    except:
                        pass
                res[head[x]] = r
                print r, x
                
            
            self.pool.get(str(val.tabel.model)).create(cr, uid, res) 

        return {}                

EksportImport()
