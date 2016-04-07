openerp.sbm_stock_split = function (instance) {
    instance.web.client_actions.add('print.stock.split', 'instance.sbm_stock_split.action');
    instance.sbm_stock_split.action = instance.web.Widget.extend({
        className: 'oe_web_example',
        init:function(parent,action){
            this._super(parent,action)
            window.open(action.params.redir, "_blank");
        },
        start: function () {
            return this._super();
        }

    });

};