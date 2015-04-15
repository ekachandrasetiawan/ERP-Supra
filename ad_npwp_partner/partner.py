from osv import osv, fields
from tools.translate import _

class partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {'npwp' : fields.char('No. NPWP', size=20, required=False, help='Misal 01.540.674.7.431-000'),}

    def onchange_format_npwp(self, cr, uid, ids, npwp):
        if npwp:
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

