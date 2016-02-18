openerp.ad_purchase_import = function (instance) {
    instance.web.client_actions.add('print.out.po.import', 'instance.ad_purchase_import.action');
    instance.ad_purchase_import.action = instance.web.Widget.extend({
        className: 'oe_web_example',
        init:function(parent,action){
            this._super(parent,action)
            // window.location = action.params.redir;
            window.open(action.params.redir, "_blank");
        },
        start: function () {
            return this._super();
        }

    });

};