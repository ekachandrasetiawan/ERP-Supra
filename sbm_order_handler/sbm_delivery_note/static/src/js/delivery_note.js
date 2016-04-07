openerp.sbm_delivery_note = function (instance) {
    instance.web.client_actions.add('print.int.move', 'instance.sbm_delivery_note.action');
    instance.sbm_delivery_note.action = instance.web.Widget.extend({
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