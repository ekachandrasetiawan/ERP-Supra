{
    "name": "Account Invoice Line Tax Amount",
    "version": "1.0",
    "depends": ["account","sbm_inherit"],
    "author": "Suprabakti Mandiri",
    "category": "Accounting & Finance",
    "description": """Modules define and saving line tax amount on invoice line, default on OpenERP each invoice lines will related to account.invoice.line.tax on each line tax defined. In account invoice line tax just only saving the key for the purpose of relation data. With this module that keys will be related as one - one on account invoice line tax amount table and saving the line tax value on each applied taxes""",
    "init_xml": [],
    'update_xml': ["account_invoice_line_tax_amount.xml"],
    'demo_xml': [],
    'installable': True,
    'active': False,
}