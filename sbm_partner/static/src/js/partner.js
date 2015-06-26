openerp.sbm_partner = function (instance) {
    instance.web.client_actions.add('print.out.exportcsv', 'instance.sbm_partner.action');
    instance.sbm_partner.action = instance.web.Widget.extend({
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