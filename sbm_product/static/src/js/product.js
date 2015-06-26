openerp.sbm_product = function (instance) {
    instance.web.client_actions.add('print.out.exportcsv', 'instance.sbm_product.action');
    instance.sbm_product.action = instance.web.Widget.extend({
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