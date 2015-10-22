{
    "name": "Inheritance Of SBM Module",
    "version": "1.0",
    "depends": [
        "purchase",
        "ad_perintah_kerja",
        "ad_delivery_note",
        "account","ad_discount",
        "ad_order_preparation",
        "web"
    ],
    "author": "Suprabakti Mandiri",
    "category": "Purchase Suprabakti",
    "description": """This module is for update openerp standart module to suprabakti mandiri
    1. Add External Doc Reference to Incoming Shipment (stock.picking.in) and validate Receive Button""",
    "init_xml": [], 
    # 'data':[
    #     'data/religion.xml'
    # ],
    'data':[
        'security/ir.model.access.csv'
    ],
    'update_xml': [
        "stock_picking.xml",
        "po.xml",
        "special_work_order.xml",
        "special_dn.xml",
        "account_invoice_line.xml",
        "account_bank_statement.xml",
        "product_batch.xml",
        "split_batch.xml",
        "supplier_first_payment.xml",
        "po_line_cancel.xml",
        "internal_move.xml",
        "super_notes.xml",
        "menu.xml",
        "sales_man_target.xml",
        "sale_order.xml",
        "setting.xml",
        # "report/faktur.xml"
        # "purchase_order.xml",
    ],
    'demo_xml': [],
    # 'demo':True,

    'installable': True,
    'active': False,
    'js':['static/src/js/account_invoice.js'],
    # "qweb": [
    #     'static/src/xml/reportbutton.xml',
    # ],
}
