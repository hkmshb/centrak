/* jshint laxcomma:true */

(function($, Backbone, _, app) {
    'use strict';

    var ProjectXFormListView = Backbone.View.extend({
        initialize: function() {
            this.$toggler = $('input.toggler');
            this.$chkColl = $('.listing input.icheckbox');
        },

        events: {
            'click input.toggler': 'togglerChanged',
            'click input.icheckbox': 'formCheckboxChanged',
            'click button.sync': 'syncSelection',
        },

        getCheckedControls: function() {
            return $('.listing input.icheckbox:checked');
        },

        togglerChanged: function(event) {
            var status = this.$toggler.is(':checked');
            this.$chkColl.each(function(){
                $(this).prop('checked', status);
            });
        },

        formCheckboxChanged: function(event) {
            var count = this.getCheckedControls().length;
            if (count == 3) {
                if (!this.$toggler.is(':checked'))
                    this.$toggler.prop('checked', true)
                                 .prop('indeterminate', false);
            } else if (count < 3 && count > 0) {
                this.$toggler.prop('checked', false)
                             .prop('indeterminate', true);
            } else {
                this.$toggler.prop('checked', false)
                             .prop('indeterminate', false);
            }
        },

        syncSelection: function(event) {
            var count = this.getCheckedControls().length;
            if (count === 0) {
                app.$fn.dialog.alert('XForm Sync', 
                    'Need to select at least 1 form to sync.');
            } else {
                $('form.xforms').submit();
            }
        }
    });

    // register views
    app.views.ProjectXFormListView = ProjectXFormListView;

})(jQuery, Backbone, _, app);