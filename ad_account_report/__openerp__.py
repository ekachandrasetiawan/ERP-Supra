{
    "name":"Accounting Report",
    "version":"0.1",
    "author":"ADSOFT",
    "website":"http://openerp.co.id",
    "category":"Custom Modules",
    "description": """
        The base module to generate excel report.
    """,
    "depends":["base", "account"],
    "init_xml":[],
    "demo_xml":[],
    "update_xml":["account_report.xml", "account_report_view.xml"],
    "active":False,
    "installable":True
}
