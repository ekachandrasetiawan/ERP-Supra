{
    "name":"Purchase Import",
    "version":"0.1",
    "author":"ADSOFT",
    "category":"Custom Modules/Purchase",
    "description": """
        The base module to generate purchase sequence.
    """,
    "depends":["base", "purchase"],
    "init_xml":[],
    "demo_xml":[],
    "update_xml":["purchase_import_view.xml"],
    "active":False,
    "installable":True,
    "js":['static/src/js/purchaseorder.js'],
}
