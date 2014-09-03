import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from tools.translate import _

class account_asset_asset(osv.osv):
    _inherit = "account.asset.asset"
    
    _columns = {
        'category_id': fields.many2one('account.asset.category', 'Asset Category', required=True, change_default=True, readonly=True, states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
    }
    
    def _compute_board_amount(self, cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=None):
        #by default amount = 0
        amount = 0
        if i == undone_dotation_number:
            amount = residual_amount
        else:
            if asset.method == 'linear':
                amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids))
                if asset.prorata:
                    amount = amount_to_depr / asset.method_number
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        amount = (amount_to_depr / asset.method_number) / total_days * days
                    elif i == undone_dotation_number:
                        amount = (amount_to_depr / asset.method_number) / total_days * (total_days - days)
#             elif asset.method == 'degressive':
#                 amount = residual_amount * asset.method_progress_factor
#                 if asset.prorata:
#                     days = total_days - float(depreciation_date.strftime('%j'))
#                     if i == 1:
#                         amount = (residual_amount * asset.method_progress_factor) / total_days * days
#                     elif i == undone_dotation_number:
#                         amount = (residual_amount * asset.method_progress_factor) / total_days * (total_days - days)
        return amount

    def compute_depreciation_board(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        currency_obj = self.pool.get('res.currency')
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.value_residual == 0.0:
                continue
            posted_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_check', '=', True)],order='depreciation_date desc')
            old_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_id', '=', False)])
            if old_depreciation_line_ids:
                depreciation_lin_obj.unlink(cr, uid, old_depreciation_line_ids, context=context)

            amount_to_depr = residual_amount = asset.value_residual
            #initiate depreciation_date
            if asset.prorata:
                depreciation_date = datetime.strptime(self._get_last_depreciation_date(cr, uid, [asset.id], context)[asset.id], '%Y-%m-%d')
            else:
                # depreciation_date = 1st January of purchase year
                purchase_date = datetime.strptime(asset.purchase_date, '%Y-%m-%d')
                #if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
                if (len(posted_depreciation_line_ids)>0):
                    last_depreciation_date = datetime.strptime(depreciation_lin_obj.browse(cr,uid,posted_depreciation_line_ids[0],context=context).depreciation_date, '%Y-%m-%d')
                    depreciation_date = (last_depreciation_date+relativedelta(months=+asset.method_period))
                else:
                    depreciation_date = datetime(purchase_date.year, purchase_date.month,1)
            #end initiate depreciation_date
            
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366

            residu_factor_amount=0.0 #penampung nominal hasil kali antara amount residu dan method_factor setiap tahunnya
            year_curr=depreciation_date.year #penampung tahun yg sedang akan dibuat
            total_residual=asset.value_residual
#             if len(posted_depreciation_line_ids)!=1:
#                 if depreciation_lin_obj.browse(cr,uid,posted_depreciation_line_ids)[0]:
#                     residu_factor_amount=depreciation_lin_obj.browse(cr,uid,posted_depreciation_line_ids)[0].amount*12
            undone_dotation_number = self._compute_board_undone_dotation_nb(cr, uid, asset, depreciation_date, total_days, context=context)
            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                i = x + 1
                if asset.method == 'linear':
                    amount = self._compute_board_amount(cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=context)
                elif asset.method == 'degressive':
                    if i==undone_dotation_number:
                        amount=residual_amount
                    else:
                        if i==1:
                            residu_factor_amount=total_residual*asset.method_progress_factor
                        if year!=year_curr:
                            year_curr=year
                            total_residual=residual_amount
                            residu_factor_amount=total_residual*asset.method_progress_factor
                        amount=residu_factor_amount/12
                company_currency = asset.company_id.currency_id.id
                current_currency = asset.currency_id.id
                # compute amount into company currency
                amount = currency_obj.compute(cr, uid, current_currency, company_currency, amount, context=context)
                residual_amount -= amount
                vals = {
                     'amount': amount,
                     'asset_id': asset.id,
                     'sequence': i,
                     'name': str(asset.id) +'/' + str(i),
                     'remaining_value': residual_amount,
                     'depreciated_value': (asset.purchase_value - asset.salvage_value) - (residual_amount + amount),
                     'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                }
                depreciation_lin_obj.create(cr, uid, vals, context=context)
                # Considering Depr. Period as months
                depreciation_date = (datetime(year, month, day) + relativedelta(months=+asset.method_period))
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year
        return True
account_asset_asset()