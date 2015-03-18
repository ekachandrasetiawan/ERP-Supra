import re
import csv
import time
import base64
import calendar
import datetime
from osv import fields, osv
import decimal_precision as dp


class ReportSaldoAkhir(osv.osv_memory):
    _name = "report.saldo.akhir"
    _columns = {
                'date_from' :fields.date('From'),
                'date_to' :fields.date('To')
    }
    _defaults = {
                'date_from': time.strftime('%Y-%m-%d'),
                'date_to': time.strftime('%Y-%m-%d'),
    }

    def eksport_report_saldo_akhir(self,cr,uid,ids,context=None):
        searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
        browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
        
        val = self.browse(cr, uid, ids)[0]
        # print '=====================================',account
        urlTo = str(browseConf.value)+"report-accounting/saldo-akhir&from="+val.date_from+"&to="+val.date_to
        
        
        return {
            'type'  : 'ir.actions.client',
            'target': 'new',
            'tag'   : 'print.out.stockmove',
            'params': {
                # 'id'  : ids[0],
                'redir' : urlTo,
                'uid':uid
            },
        }

ReportSaldoAkhir()


class ReportTransaksiAccount(osv.osv_memory):
    _name = "report.transaksi.account"
    _columns = {
                'date_from' : fields.date('From'),
                'date_to' : fields.date('To'),
                'name': fields.many2many('account.account', 'pre_account_rel', 'account_id', 'name_id', 'Data Account'),
    }
    _defaults = {
                'date_from': time.strftime('%Y-%m-%d'),
                'date_to': time.strftime('%Y-%m-%d'),
    }

    def eksport_report_transaksi_account(self,cr,uid,ids,context=None):
        searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
        browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
        
        val = self.browse(cr, uid, ids)[0]
        # account=str(val.name.id)
        print '========================',val.name
        # idacc= []
        # for x in val.name:
        #     idacc = x.id

        print '==============================',idacc
        # print '=====================================',account
        urlTo = str(browseConf.value)+"report-accounting/transaksi-account&account="+account+"&from="+val.date_from+"&to="+val.date_to
        
        
        return {
            'type'  : 'ir.actions.client',
            'target': 'new',
            'tag'   : 'print.out.stockmove',
            'params': {
                # 'id'  : ids[0],
                'redir' : urlTo,
                'uid':uid
            },
        }

ReportTransaksiAccount()


class AccountAccount(osv.osv_memory):
    _inherit = 'account.account'
    _name = 'account.account'

    _columns = {
        'account': fields.many2many('report.transaksi.account', 'pre_account_rel', 'name_id', 'account_id', 'Account'),
    }

AccountAccount()


class MutasiStock(osv.osv_memory):
    _name = "mutasi.stock"
    _columns = {
                'date_from' : fields.date('From'),
                'date_to' : fields.date('To'),
                'data_eksport': fields.binary('File', readonly=True),
                'name': fields.char('File Name', 16),
                'report': fields.selection((('del','Delivery Order'), ('inc','Incoming Shipment')), 'Report'),
    }   
    
    _defaults = {
                'report': 'del',
                'date_from': time.strftime('%Y-%m-%d'),
                'date_to': time.strftime('%Y-%m-%d'),
    }   

    def eksport_excel(self,cr,uid,ids,context=None):
        searchConf = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'base.print')], context=context)
        browseConf = self.pool.get('ir.config_parameter').browse(cr,uid,searchConf,context=context)[0]
        
        val = self.browse(cr, uid, ids)[0] 
        # print '=====================================',val.report
        urlTo = str(browseConf.value)+"report-accounting/stock-move&jenis="+val.report+"&from="+val.date_from+"&to="+val.date_to
        
        
        return {
            'type'  : 'ir.actions.client',
            'target': 'new',
            'tag'   : 'print.out.stockmove',
            'params': {
                # 'id'  : ids[0],
                'redir' : urlTo,
                'uid':uid
            },
        }

    # def eksport_excel(self, cr, uid, ids, context=None):
    #     val = self.browse(cr, uid, ids)[0] 
        
    #     # No.DO, No.SJ, customer, No.Invoice customer
               
    #     tipe = 'out'
    #     title = 'deliver.csv'
    #     data = 'sep=;\nPart Name;Code Name;PO Customer;Date;Delivery Note;Delivery Order;Customer;Quantity;Price;Total'
        
    #     if val.report == 'inc':
    #         tipe = 'in'
    #         title = 'incoming.csv'
    #         data = 'sep=;\nPart Name;Code Name;Purchase Order;Receiving Report;Date;Supplier;Quantity;Price;Total'
                
    #     res = self.pool.get('stock.picking').search(cr, uid, [('type', '=', tipe), ('state', '=', 'done'), ('date', '>=', val.date_from), ('date', '<=',  val.date_to)])
    #     result = self.pool.get('stock.picking').browse(cr, uid, res) 
         
    #     if val.report == 'del':
    #         for row in result:
    #             for move in row.move_lines:
    #                 price = move.sale_line_id.price_unit or 0
    #                 subtotal = move.product_qty * price
    #                 ori = '-'
    #                 if move.sale_line_id.order_id:
    #                     ori = move.sale_line_id.order_id.client_order_ref
    #                 d = [move.product_id.name_template, 
    #                      move.product_id.default_code,
    #                      str(ori),
    #                      str(row.date),
    #                      str(row.note_id.name),
    #                      str(row.note_id.prepare_id.name),
    #                      str(row.partner_id.name), 
    #                      str(move.product_qty).replace('.',','), 
    #                      str(move.sale_line_id.price_unit).replace('.',','), 
    #                      str(subtotal).replace('.',',')]  
    #                 data += '\n' + ';'.join(d)
                    
    #     elif val.report == 'inc':
    #         for row in result:
    #             for move in row.move_lines:
    #                 price = move.purchase_line_id.price_unit or 0
    #                 subtotal = move.product_qty * price
    #                 d = [move.product_id.name_template, 
    #                      move.product_id.default_code,
    #                      str(row.purchase_id.name), 
    #                      str(row.name), 
    #                      str(row.date),
    #                      str(row.partner_id.name), 
    #                      str(move.product_qty).replace('.',','), 
    #                      str(move.purchase_line_id.price_unit).replace('.',','), 
    #                      str(subtotal).replace('.',',')]  
    #                 data += '\n' + ';'.join(d) 
                    
    #     out = base64.b64encode(data.encode('ascii',errors='ignore'))
    #     self.write(cr, uid, ids, {'data_eksport':out, 'name':title}, context=context)
        
    #     view_rec = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ad_mutasi_stock', 'view_wizard_mutasi_stock')
    #     view_id = view_rec[1] or False
        
    #     return {
    #         'view_type': 'form',
    #         'view_id' : [view_id],
    #         'view_mode': 'form',
    #         'res_id': val.id, 
    #         'res_model': 'mutasi.stock', # Object wizard terkait
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #     }

    
MutasiStock()



