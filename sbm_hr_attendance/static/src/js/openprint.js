openerp.sbm_hr_attendance = function (instance) {
    instance.web.client_actions.add('print.out', 'instance.sbm_hr_attendance.action');
    instance.sbm_hr_attendance.action = instance.web.Widget.extend({
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