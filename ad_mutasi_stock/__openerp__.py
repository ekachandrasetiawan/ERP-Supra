{
    "name":"Mutasi Stock Report",
    "version":"0.1",
    "author":"ADSOFT",
    "category":"Custom Modules",
    "description": """
        The base module to generate excel report.
    """,
    "depends":["base", "account", "stock"],
    "init_xml":[],
    "demo_xml":[],
    "update_xml":["mutasi_stock_view.xml"],
    "active":False,
    "installable":True,
    'certificate': '',
    'js':['static/src/js/mutasi_stock.js']
}