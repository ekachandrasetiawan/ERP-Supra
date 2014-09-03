# -*- encoding: utf-8 -*-


{
    "name": "Delivery Orders Consolidation",
    "author": "ADSOFT",
    "Description": """
    This module adds a facility to merge several Delivery Orders of the same Customer
    """,
    "version": "0.1",
    "depends": ["stock", "account", "sale", "base"],
    "category" : "Tools",
    "init_xml": [],
    "update_xml": [
        'merge_pickings_view.xml',
    ],
    "demo_xml": [],
    "test": [],
    "installable": True,
    "active": False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
