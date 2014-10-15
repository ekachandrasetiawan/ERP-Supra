{
    "name": "Inheritance Of SBM Module",
    "version": "1.0",
    "depends": [
        "purchase",
        "ad_perintah_kerja",
        "ad_delivery_note",
        "account","ad_discount",
        "ad_order_preparation",
    ],
    "author": "Suprabakti Mandiri",
    "category": "Purchase Suprabakti",
    "description": """This module is for update openerp standart module to suprabakti mandiri
    1. Add External Doc Reference to Incoming Shipment (stock.picking.in) and validate Receive Button""",
    "init_xml": [], 
    'update_xml': [
        "stock_picking.xml",
        "po.xml",
        "special_work_order.xml",
        "special_dn.xml",
        "account_invoice_line.xml",
        "account_bank_statement.xml",
        "product_batch.xml",
        "split_batch.xml",
        # "report/faktur.xml"
        # "purchase_order.xml",
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}