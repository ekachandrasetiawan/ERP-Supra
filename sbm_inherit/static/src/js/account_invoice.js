openerp.sbm_inherit = function (instance) {
    instance.web.client_actions.add('print.out', 'instance.sbm_inherit.action');
    instance.sbm_inherit.action = instance.web.Widget.extend({
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