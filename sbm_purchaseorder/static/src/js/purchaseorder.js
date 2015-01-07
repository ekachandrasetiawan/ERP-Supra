openerp.sbm_purchaseorder = function (instance) {
    instance.web.client_actions.add('print.out.po', 'instance.sbm_purchaseorder.action');
    instance.sbm_purchaseorder.action = instance.web.Widget.extend({
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