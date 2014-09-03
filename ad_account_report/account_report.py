import re
import csv
import time
import base64
import calendar
import datetime
from osv import fields, osv
import decimal_precision as dp

class MutasiAccount(osv.osv_memory):
    _name = "mutasi.account"
    _columns = {
                'account_from': fields.many2one('account.account', 'Account From', required=True, domain=[('type','<>','view')]),
                'account_to': fields.many2one('account.account', 'Account To', required=True, domain=[('type','<>','view')]),
                'date_from' : fields.date('Date From'),
                'date_to' : fields.date('Date To'),
    }   
    
    _defaults = {
                'date_from': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
                'date_to': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }   
        
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'mutasi.account'
        datas['form'] = self.read(cr, uid, ids)[0]
 
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'mutasi.report',
            'report_type': 'webkit',
            'datas': datas,
        }
               
    
MutasiAccount()


class ReportVoucher(osv.osv_memory):
    _name = "many.voucher"
    _columns = {
                'name': fields.char('Name', 16),
                'statement_id': fields.many2one('account.bank.statement', 'Statement', required=True),
                'line_ids': fields.many2many('account.bank.statement.line', 'statement_line_rel', 'statement_line_id', 'statement_id', 'Voucher', required=True, domain="[('statement_id','=',statement_id)]"),
    }   
        
    def print_voucher(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {'ids': [data['id']]}
        datas['model'] = 'account.bank.statement'
        datas['form'] = data
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'laporan.voucher',
            'nodestroy': True,
            'datas': datas,
        }

ReportVoucher()

class AccountLegal(osv.osv_memory):
    _name = "accounting.legal"
    _columns = {
                'report': fields.selection((('gl','General Ledger'), ('tb','Trial Balance'), ('bs','Balance Sheet'), ('pl','Profit Loss')), 'Report'),
                'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', required=True),
                'period_from': fields.many2one('account.period', 'Start Period', domain="[('fiscalyear_id', '=', fiscalyear_id)]", required=True),
                'period_to': fields.many2one('account.period', 'End Period', domain="[('fiscalyear_id', '=', fiscalyear_id)]", required=True),
                'name': fields.char('File Name', 16),               
    }   
    
    _defaults = {
                'report': 'tb',
                'fiscalyear_id':1,
                'period_from': 2,
                'period_to': 12,
    }   
         
    def eksport_excel(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        if val.period_from.id > val.period_to.id:
            raise osv.except_osv(('Error'), ('Start period should be smaller then End period'))
        openclose_journal = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'situation')])
        
        data = [] 
        if val.report == 'gl' or val.report == 'tb':
            title = 'trial.balance.excel'
            ids_acc = self.pool.get('account.account')._get_children_and_consol(cr, uid, [1])
            acc_data = self.pool.get('account.account').browse(cr, uid, ids_acc)
             
            mid = self.pool.get('account.move').search(cr, uid, [('state', '=', 'posted'), ('journal_id', 'not in', tuple(openclose_journal)), ('period_id', '>=', val.period_from.id), ('period_id', '<=',  val.period_to.id)])
          
            for acc in acc_data:
                mutasi = (0, 0)
                anak = False
                initial = self.amount_initial(cr, uid, ids, acc, openclose_journal, val.fiscalyear_id)
                opening = self.mutasi_period(cr, uid, ids, acc, val.fiscalyear_id, val.period_from.id, openclose_journal)
                if acc.type == 'view':
                    mutasi = self.amount_parent(cr, uid, ids, acc, mid)
                else:
                    anak = True
                    mutasi = self.amount_child(cr, uid, ids, acc, mid)
                data.append([
                             acc.code, 
                             acc.name,'-',
                             str((initial[0]+opening[0])-(initial[1]+opening[1])).replace('.',','),
                             str(mutasi[0]).replace('.',','),
                             str(mutasi[1]).replace('.',','),
                             str(((initial[0]+opening[0])-(initial[1]+opening[1]))+mutasi[0]-mutasi[1]).replace('.',',')
                            ])  
                
                if acc.currency_id:
                    fored = 0; forec = 0
                    buka = (initial[3]+opening[3])-(initial[4]+opening[4])
                    for fore in mutasi[2]:
                        if fore['amount_currency'] < 0:
                            forec += fore['amount_currency']
                        else:
                            fored += fore['amount_currency']
                    data.append([
                                 'original',
                                 'currency', acc.currency_id.name,
                                 str(buka).replace('.',','),
                                 str(fored).replace('.',','),
                                 str(abs(forec)).replace('.',','),
                                 str(buka+fored-abs(forec)).replace('.',',')
                                ])
                    
                if val.report == 'gl':
                    title = 'general.ledger.excel'
                    if anak: 
                        mutasi[2].sort(key=lambda tup: tup['date'])   
                        bal = (initial[0]+opening[0])-(initial[1]+opening[1])
                        for a in mutasi[2]:
                            bal += a['debit']; bal -= a['credit']
                            data.append([
                                         a['date'], 
                                         a['ref'],
                                         a['name'],'0',
                                         str(a['debit']).replace('.',','),
                                         str(a['credit']).replace('.',','),
                                         str(bal).replace('.',','),
                                         str(a['amount_currency']).replace('.',',')
                                        ])
                            
        elif val.report == 'bs':
            title = 'balance.sheet.excel'
            bsid = self.pool.get('account.account').search(cr, uid, [('name', '=', 'BALANCE SHEET')])
            if not bsid:
                raise osv.except_osv(('Error'), ('You must create BALANCE SHEET account'))
             
            ids_acc = self.pool.get('account.account')._get_children_and_consol(cr, uid, [bsid[0]])
            acc_data = self.pool.get('account.account').browse(cr, uid, ids_acc)
             
            mid = self.pool.get('account.move').search(cr, uid, [('state', '=', 'posted'), ('period_id', 'in', tuple([x.id for x in val.fiscalyear_id.period_ids if x.id <= val.period_from.id]))])
            mod = self.pool.get('account.move').search(cr, uid, [('state', '=', 'posted'), ('journal_id', 'not in', tuple(openclose_journal)), ('period_id', '>=', val.period_from.id), ('period_id', '<=',  val.period_to.id)])         
 
             
            for acc in acc_data:
                if acc.type == 'view':
                    ending = self.amount_parent(cr, uid, ids, acc, mid)
                    data.append([
                                 acc.code, 
                                 acc.name,
                                 str(ending[0]-ending[1]).replace('.',',')
                                ])
 
            plid = self.pool.get('account.account').search(cr, uid, [('name', '=', 'PROFIT LOSS')])
            if not plid:
                raise osv.except_osv(('Error'), ('You must create PROFIT LOSS account'))
             
            pl_data = self.pool.get('account.account').browse(cr, uid, plid[0])
            akhir = self.amount_parent(cr, uid, ids, pl_data, mid)
            transaksi = self.amount_parent(cr, uid, ids, pl_data, mod)
            data.append([pl_data.code, pl_data.name, str(akhir[0]-akhir[1]).replace('.',',')])              
 
        elif val.report == 'pl':
            title = 'profit.loss.excel'
             
            plid = self.pool.get('account.account').search(cr, uid, [('name', '=', 'PROFIT LOSS')])
            if not plid:
                raise osv.except_osv(('Error'), ('You must create PROFIT LOSS account'))
             
            ids_acc = self.pool.get('account.account')._get_children_and_consol(cr, uid, [plid[0]])
            acc_data = self.pool.get('account.account').browse(cr, uid, ids_acc)
             
            mid = self.pool.get('account.move').search(cr, uid, [('state', '=', 'posted'), ('period_id', 'in', tuple([x.id for x in val.fiscalyear_id.period_ids if x.id <= val.period_from.id]))])
            mod = self.pool.get('account.move').search(cr, uid, [('state', '=', 'posted'), ('journal_id', 'not in', tuple(openclose_journal)), ('period_id', '>=', val.period_from.id), ('period_id', '<=',  val.period_to.id)])         
 
            for acc in acc_data:
                if acc.type == 'view':
                    ending = self.amount_parent(cr, uid, ids, acc, mid)
                    mutasi = self.amount_parent(cr, uid, ids, acc, mod)
                else:
                    ending = self.amount_child(cr, uid, ids, acc, mid)
                    mutasi = self.amount_child(cr, uid, ids, acc, mod)
                data.append([
                             acc.code, 
                             acc.name,
                             str(mutasi[0]-mutasi[1]).replace('.',','),
                             str(ending[0]-ending[1]).replace('.',',')
                            ])  
                
        
        if context is None:
            context = {}
        nilai = self.read(cr, uid, ids)[0]
        datas = {'ids': [nilai['id']]}
        datas['model'] = 'accounting.legal'
        datas['form'] = nilai
        datas['csv'] = data
        
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': title,
            'nodestroy': True,
            'datas': datas,
        }
        
    def mutasi_period(self, cr, uid, ids, account, fiscal, period, journal):
        prd = [x.id for x in fiscal.period_ids if x.id < period]
        mod = self.pool.get('account.move').search(cr, uid, [('state', '=', 'posted'), ('period_id', 'in', tuple(prd)), ('journal_id', 'not in', tuple(journal))])
        if account.type == 'view':
            res = self.amount_parent(cr, uid, ids, account, mod)
        else:
            res = self.amount_child(cr, uid, ids, account, mod)
        return res
    
    def amount_initial(self, cr, uid, ids, account, journal, fiscal):
        res = (0,0,[],0,0)
        period = [x.id for x in fiscal.period_ids]
        mod = self.pool.get('account.move').search(cr, uid, [('state', '=', 'posted'), ('period_id', 'in', tuple(period)), ('journal_id', 'in', tuple(journal))])
        if account.type == 'view':
            res = self.amount_parent(cr, uid, ids, account, mod)
        else:
            res = self.amount_child(cr, uid, ids, account, mod)
        return res
    
    def amount_parent(self, cr, uid, ids, account, move):
        ids_acc = self.pool.get('account.account')._get_children_and_consol(cr, uid, [account.id])
        acc_data = self.pool.get('account.account').browse(cr, uid, ids_acc)
        debit = 0; credit = 0; fored = 0; forec = 0
        for a in acc_data:
            if a.type != 'view':
                res = self.amount_child(cr, uid, ids, a, move)
                debit += res[0]
                credit += res[1]
                fored += res[3]
                forec += res[4]
        return (debit, credit, [], fored, forec)

    def amount_child(self, cr, uid, ids, account, move):
        lid = self.pool.get('account.move.line').search(cr, uid, [('move_id', 'in', move), ('account_id', '=', account.id)])
        lad = self.pool.get('account.move.line').browse(cr, uid, lid)
        debit = sum([x.debit for x in lad])
        credit = sum([x.credit for x in lad])

        fored = 0; forec = 0
        if account.currency_id:
            for f in lad:
                if f.debit :
                    fored += abs(f.amount_currency)
                else:
                    forec += abs(f.amount_currency)

        transaksi = []
        if lad:
            for a in lad:
                nama = a.move_id.name
                if a.statement_id:
                    urut = int((a.move_id.name).split('/')[-1])
                    sid = self.pool.get('account.bank.statement.line').search(cr, uid, [('statement_id', '=', a.statement_id.id), ('sequence', '=', urut)])
                    sad = self.pool.get('account.bank.statement.line').browse(cr, uid, sid)
                    nama = sad[0].code_voucher
                transaksi.append({
                                  'date': a.move_id.date,
                                  'ref': a.name,
                                  'name': nama,
                                  'debit': a.debit,
                                  'credit': a.credit,
                                  'amount_currency': a.amount_currency
                                  })
        return (debit, credit, transaksi, fored, forec)
    
AccountLegal()


