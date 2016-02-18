{
    "name": "SBM Delivery Note",
    "version": "1.0",
    "depends": [ 
                "sale", 
                "stock", 
                "product", 
                "ad_order_preparation",
                "sbm_order_preparation",
                "ad_delivery_note",
                "new_sbm_sale_order"],
    "author": "PT.Suprabakti Mandiri",
    "category": "Module Delivery Note",
    "description": """ Module Delivey Note Suprabakti Mandiri""",
    "init_xml": [],
    "update_xml":['sbm_delivery_note_view.xml','setting.xml','search.xml','support/support.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'certificate': '',
    'js':['static/src/js/delivery_note.js'],
}


