openerp.sbm_work_order = function (instance) {
    instance.web.client_actions.add('print.adhoc.order.request', 'instance.sbm_work_order.action');
    instance.sbm_work_order.action = instance.web.Widget.extend({
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