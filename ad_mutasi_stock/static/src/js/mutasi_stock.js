openerp.ad_mutasi_stock = function (instance) {
    instance.web.client_actions.add('print.out.stockmove', 'instance.ad_mutasi_stock.action');
    instance.ad_mutasi_stock.action = instance.web.Widget.extend({
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