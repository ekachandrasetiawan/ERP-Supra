{
    "name": "Order Requisition Delivery",
    "version": "1.0", 
    "depends": [
                "base",
                "purchase",
                "hr",
                "product",
                "stock",
                "sbm_purchaseorder"
                ],
    "author": "Supra Bakti Mandiri",
    "category": "Order Requisition Delivery",
    "description":"""
        Proses Distribusi Barang - Barang Purchasing untuk mengurangi stock
    """,
    "data":['order_requisition_delivery_view.xml','setting.xml','menu.xml'],
    "demo":[],
    "installable":True,
    "active":False,
}