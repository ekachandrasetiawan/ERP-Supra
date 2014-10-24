openerp.sbm_web_example = function (instance) {
    instance.web.client_actions.add('example.action', 'instance.sbm_web_example.action');
    instance.sbm_web_example.action = instance.web.Widget.extend({
        className: 'oe_web_example',
        /*start: function () {
            this.$el.text("Hello, world!");

            return this._super();
        }*/
        // render dengan template,
        // template: 'sbm_web_example.action',
        start:function(){
        	console.log(this.dataset.ids)
        }

    });

};