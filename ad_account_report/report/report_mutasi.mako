import re
import time
import pooler
import xlwt
from osv import osv
from report import report_sxw
from report_engine_xls import report_xls

class ReportStatus(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(ReportStatus, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'koma': self.FormatWithCommas,
            'get_basedon': self.get_basedon,
            'get_account': self.get_account,
            'get_initial': self.get_initial,
            'negatif': self.negatif,
            'positif': self.positif,
            'get_voucher': self.get_voucher,
            'get_line': self.get_line,
            'get_amount': self.get_amount,
            'get_no': self.get_no,
            'get_header': self.get_header,
            
        })

        self.re_digits_nondigits = re.compile(r'\d+|\D+')
            

        self.no = 0
        
    def get_no(self):
        self.no = self.no + 1
        return self.no 
    
    def negatif(self, num):
        con = 0
        if num < 0 :
            con = num
        return con
    
    def positif(self, num):
        con = 0
        if num > 0 :
            con = num
        return con 

    def get_amount(self, o):
        db = 0; kr = 0
        for x in o.line_ids:
            if x.amount < 0:
                kr += x.amount
            else:
                db += x.amount
        
        return (db, kr)

    def get_header(self, o):
        data =[(o.statement_id.journal_id.type).upper() + ' VOUCHER']
        vch = [x.name for x in o.line_ids]
        data.append(vch[0])
        return data

    def get_initial(self, account, form):
        datefrom = form['form']['date_from'] 
        
        move_line_obj = self.pool.get('account.move.line')
        
        idac = move_line_obj.search(self.cr, self.uid, [('account_id', '=', account.id), ('date', '<',  datefrom)])
        data = move_line_obj.browse(self.cr, self.uid, idac)
        debit = 0; credit = 0
        
        for x in data:
            debit += x.debit
            credit += x.credit

        openclose_journal = self.pool.get('account.journal').search(self.cr, self.uid, [('type', '=', 'situation')])
        mod = self.pool.get('account.move').search(self.cr, self.uid, [('state', '=', 'posted'), ('journal_id', 'in', tuple(openclose_journal))])         

        inac = move_line_obj.search(self.cr, self.uid, [('account_id', '=', account.id), ('move_id', 'in',  tuple(mod))])
        daac = move_line_obj.browse(self.cr, self.uid, inac)
        
        for i in daac:
            debit += i.debit
            credit += i.credit

        return debit-credit
        
    def get_line(self, account, form):
        datefrom = form['form']['date_from'] 
        dateto = form['form']['date_to']
        idac = self.pool.get('account.move.line').search(self.cr, self.uid, [('account_id', '=', account.id), ('journal_id', 'not in', (6, 12, 13)), ('date', '>=', datefrom), ('date', '<=',  dateto)])
        data = self.pool.get('account.move.line').browse(self.cr, self.uid, idac)
        return data
    
    def get_basedon(self, form):
        data = self.pool.get(form['model']).browse(self.cr, self.uid, [form['form']['id']])
        return data

    def get_voucher(self, sti, ref, move):
        data = move
        if sti:
           did = self.pool.get('account.bank.statement.line').search(self.cr, self.uid, [('statement_id', '=', sti), ('ref', '=', ref)])
           if did:
               dad = self.pool.get('account.bank.statement.line').browse(self.cr, self.uid, did[0])
               data = dad.code_voucher
        return data
    
    def get_account(self, form):
        acc = [x for x in range(form['form']['account_from'][0], form['form']['account_to'][0]+1)]
        data = self.pool.get('account.account').browse(self.cr, self.uid, acc)
        return data
                           
    def FormatWithCommas(self, format, value):
        parts = self.re_digits_nondigits.findall(format % (value,))
        for i in xrange(len(parts)):
            s = parts[i]
            if s.isdigit():
                parts[i] = self.commafy(s)
                break
        return ''.join(parts)
        
    def commafy(self, s):
        r = []
        for i, c in enumerate(reversed(s)):
            if i and (not (i % 3)):
                r.insert(0, ',')
            r.insert(0, c)
        return ''.join(r)


report_sxw.report_sxw('report.laporan.voucher', 'many.voucher', 'addons/ad_account_report/report/laporan_voucher.rml', parser=ReportStatus, header=False)        
report_sxw.report_sxw('report.mutasi.report', 'account.move', 'addons/ad_account_report/report/report_mutasi.mako', parser=ReportStatus, header=False)
       

class general_ledger_xls(report_xls):

    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('General Ledger'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1

        cols_specs = [
                      ('Account Code', 1, 70, 'text', lambda x, d, p: x[0]),
                      ('Account Name', 1, 120, 'text', lambda x, d, p: x[1]),
                      ('Refference', 1, 70, 'text', lambda x, d, p: x[2]),
                      ('Opening Balance', 1, 100, 'text', lambda x, d, p: x[3]),
                      ('Debit', 1, 100, 'text', lambda x, d, p: x[4]),
                      ('Credit', 1, 100, 'text', lambda x, d, p: x[5]),
                      ('Ending Balance', 1, 100, 'text', lambda x, d, p: x[6]),
        ]
       
        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;')
        title = self.xls_row_template(cols_specs, ['Account Code', 'Account Name', 'Refference', 'Opening Balance', 'Debit', 'Credit', 'Ending Balance'])
        self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
        
        
        row_count = 1
        for x in data['csv']:
            ws.write(row_count, 0, x[0])
            ws.write(row_count, 1, x[1])
            ws.write(row_count, 2, x[2])
            ws.write(row_count, 3, x[3])
            ws.write(row_count, 4, x[4])
            ws.write(row_count, 5, x[5])
            ws.write(row_count, 6, x[6])
            row_count += 1
            
        pass

general_ledger_xls('report.general.ledger.excel', 'account.move', 'addons/ad_account_report/report/report_mutasi.mako', parser=ReportStatus, header=False)


class trial_balance_xls(report_xls):

    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Trial Balance'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1

        cols_specs = [
                      ('Account Code', 1, 70, 'text', lambda x, d, p: x[0]),
                      ('Account Name', 1, 120, 'text', lambda x, d, p: x[1]),
                      ('Opening Balance', 1, 100, 'text', lambda x, d, p: x[2]),
                      ('Debit', 1, 100, 'text', lambda x, d, p: x[3]),
                      ('Credit', 1, 100, 'text', lambda x, d, p: x[4]),
                      ('Ending Balance', 1, 100, 'text', lambda x, d, p: x[5]),
        ]
       
        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;')
        title = self.xls_row_template(cols_specs, ['Account Code', 'Account Name', 'Opening Balance', 'Debit', 'Credit', 'Ending Balance'])
        self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
        
        
        row_count = 1
        for x in data['csv']:
            ws.write(row_count, 0, x[0])
            ws.write(row_count, 1, x[1])
            ws.write(row_count, 2, x[3])
            ws.write(row_count, 3, x[4])
            ws.write(row_count, 4, x[5])
            ws.write(row_count, 5, x[6])
            row_count += 1
            
        pass

trial_balance_xls('report.trial.balance.excel', 'account.move', 'addons/ad_account_report/report/report_mutasi.mako', parser=ReportStatus, header=False)


class balance_sheet_xls(report_xls):

    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Balance Sheet'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1

        cols_specs = [
                      ('Account Code', 1, 70, 'text', lambda x, d, p: x[0]),
                      ('Account Name', 1, 120, 'text', lambda x, d, p: x[1]),
                      ('Ending Balance', 1, 100, 'text', lambda x, d, p: x[2]),
        ]
       
        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;')
        title = self.xls_row_template(cols_specs, ['Account Code', 'Account Name', 'Ending Balance'])
        self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
        
        
        row_count = 1
        for x in data['csv']:
            ws.write(row_count, 0, x[0])
            ws.write(row_count, 1, x[1])
            ws.write(row_count, 2, x[2])
            row_count += 1
            
        pass

balance_sheet_xls('report.balance.sheet.excel', 'account.move', 'addons/ad_account_report/report/report_mutasi.mako', parser=ReportStatus, header=False)


class profit_loss_xls(report_xls):

    def generate_xls_report(self, parser, data, obj, wb):
        ws = wb.add_sheet(('Balance Sheet'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1

        cols_specs = [
                      ('Account Code', 1, 70, 'text', lambda x, d, p: x[0]),
                      ('Account Name', 1, 150, 'text', lambda x, d, p: x[1]),
                      ('Transaction of Month', 1, 100, 'text', lambda x, d, p: x[2]),
                      ('Ending Balance', 1, 100, 'text', lambda x, d, p: x[3]),
        ]
       
        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;')
        title = self.xls_row_template(cols_specs, ['Account Code', 'Account Name', 'Transaction of Month', 'Ending Balance'])
        self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
        
        row_count = 1
        for x in data['csv']:
            ws.write(row_count, 0, x[0])
            ws.write(row_count, 1, x[1])
            ws.write(row_count, 2, x[2])
            ws.write(row_count, 3, x[3])
            row_count += 1
            
        pass

profit_loss_xls('report.profit.loss.excel', 'account.move', 'addons/ad_account_report/report/report_mutasi.mako', parser=ReportStatus, header=False)

