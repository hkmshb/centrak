/* jshint: laxcomma:true */

(function($, Backbone, _, app) {
    'use strict';

    // ::: views :::
    var AdminOrganisationForm = Backbone.View.extend({
        el: '.content-pane',
        events: {
            'click button.save': 'submit'
        },
        submit: function() {
            $('form', this.$el).submit();
        },
        serializeForm: function(form) {
            return _.object(_.map(form.serializeArray(), function(item) {
                return [item.name, item.value];
            }));
        }
    });    

    // ::: registery
    app.views.AdminOrganisationForm = AdminOrganisationForm;

})(jQuery, Backbone, _, app);