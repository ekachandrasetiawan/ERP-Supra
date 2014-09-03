openerp.visual_export = function (instance) {

    var _t = instance.web._t;
    var QWeb = instance.web.qweb;

    instance.web.ListView.include({
        load_list: function () {
            var self = this;
            var add_button = false;
            if (!this.$buttons) {
                add_button = true;
            }
            this._super.apply(this, arguments);
            if(add_button) {
                this.$buttons.on('click', '.oe_list_button_export', function() {
                    fields_and_headers = self.get_export_fields_and_headers();
                    $.blockUI();
                    self.session.get_file({
                        url: '/web/export/spreadsheet_view',
                        data: {data: JSON.stringify({
                            model: self.model,
                            fields: fields_and_headers[0],
                            headers: fields_and_headers[1],
                            domain: self.groups.datagroup.domain,
                            groupby: self.groups.datagroup.group_by,
                            grouped: self.grouped,
                            view_type: self.view_type,
                            other_filter: self.get_export_other_filter(),
                            title: self.options.action.name,
                            context: self.groups.datagroup.context,
                            view_mode: 'list'
                        })},
                        complete: $.unblockUI
                    });
                });
            }
        },
        get_export_fields_and_headers: function(){
            var fields = [];
            var headers = [];
            _(this.visible_columns).each(function(c){
                if (c.name) fields.push(c.name);
                headers.push(c.string);
            });
            return [fields, headers];
        },
        get_export_other_filter: function(){
            return {};
        },
    });
    instance.web.TreeView.include({
        load_tree: function () {
            var self = this;
            var add_button = false;
            if (!this.$buttons) {
                this.$buttons = $(QWeb.render("ListView.buttons", {'widget':self}));
                if (this.options.$buttons) {
                    this.$buttons.appendTo(this.options.$buttons);
                } else {
                    this.$el.find('.oe_list_buttons').replaceWith(this.$buttons);  
                }
                add_button = true;
            }
            this._super.apply(this, arguments);
            if(add_button) {
                this.$buttons.on('click', '.oe_list_button_export', function() {
                    fields_and_headers = self.get_export_fields_and_headers();
                    $.blockUI();
                    self.session.get_file({
                        url: '/web/export/spreadsheet_view',
                        data: {data: JSON.stringify({
                            model: self.model,
                            fields: fields_and_headers[0],
                            headers: fields_and_headers[1],
                            view_type: self.view_type,
                            other_filter: self.get_export_other_filter(),
                            title: self.options.action.name,
                            view_mode: 'tree',
                            child_field: self.get_export_child_field(),
                            domain: self.dataset.domain,
                            context: self.dataset.context
                        })},
                        complete: $.unblockUI
                    });
                });
            }
        },
        get_export_fields_and_headers: function(){
            var fields = [];
            var headers = [];
            var self = this;
            _(this.fields_view.arch.children).each(function(c){
                if (!c.attrs.modifiers.tree_invisible){
                    fields.push(c.attrs.name);
                    headers.push(c.attrs.string || self.fields[c.attrs.name].string);
                }
            });
            return [fields, headers];
        },
        get_export_other_filter: function(){
            var $select = this.$el.find('select') 
            var $option = $select.find(':selected');
            res = {id: $option.val()};
            return res;
        },
        get_export_child_field: function(){
            return this.children_field;
        },
    });
};
