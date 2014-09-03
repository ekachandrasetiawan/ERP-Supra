{
    "name": "Purchase Subcont",
    "version": "1.0",
    "depends": ["base","stock","purchase",'mrp','account_voucher','sbm_purchase_rent'],
    "author": "ADSOFT",
    "category": "Complex",
    "description": """ To Manage Purchase Requitiotion, Purchase Order, Delivery Order, and Incoming Shipment
    for Subcont Project Management """,
    "init_xml": [],
    'data': [
        'purchase_subcont_view.xml',
        'purchase_requisition_subcont_view.xml',
        'wizard/purchase_order_from_requisition_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
