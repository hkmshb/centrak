/* jshint laxcomma:true */

(function($, Backbone, _, app){
    'use strict';

    var DefaultRouter = Backbone.Router.extend({
        initialize: function(options) {
            this.contentElement = '.app';
            this.current = null;
            Backbone.history.start();
        },

        render: function(view) {
            if (this.current) {
                this.current.undelegateEvents();
                this.current.$el = $();
                this.current.remove();
            }
            this.current = view;
            this.current.render();
        },

        ProjectsXFormList: function() {
            var view = new app.views.ProjectXFormListView({el: this.contentElement});
            this.render(view);
        }
    }),
    
    RouterFactory = function(rname, vname) {
        return {
            r: null,
            route: function() {
                if (_.isEmpty(this.r)) {
                    this.r = new DefaultRouter();
                    this.r[vname]();
                }
            }
        };
    };

    app.router = RouterFactory;

})(jQuery, Backbone, _, app);