from osv import osv,fields

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def print_fp(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        x = {'ids':context.get('active_ids',[])}
        x['model'] = 'account.invoice'
        x['form'] = self.read(cr,uid,ids)[0]
        o = self.pool.get('account.invoice').browse(cr,uid,ids)[0]
        if o.currency_id!=o.company_id.currency_id:
            diction = {
                'type': 'ir.actions.report.xml',
                'report_name': 'faktur.pajak.valas.form',
                'report_type': 'webkit',
                'datas': x,
            }
        else:
            diction = {
                'type': 'ir.actions.report.xml',
                'report_name': 'faktur.pajak.form',
                'report_type': 'webkit',
                'datas': x,
            }
        print "sssssssssssssssssssssssss",diction
        return diction
account_invoice()