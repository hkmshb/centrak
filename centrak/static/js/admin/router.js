(function($, Backbone, _, app) {
    'use strict';
    
    var AppRouter = Backbone.Router.extend({
        initialize: function(options) {
            this.contentElement = '.app-view';
            this.current = null;
            Backbone.history.start();
        },
        apiservice: function() {
            var view = new app.views.ApiServiceView({el: this.contentElement});
            this.render(view);
        },
        adminXforms: function() {
            var view = new app.views.AdminXFormView({el: this.contentElement});
            this.render(view);
        },
        render: function(view) {
            if (this.current) {
                this.current.undelegateEvents();
                this.current.$el = $();
                this.current.remove();
            }
            
            this.current = view;
            this.current.render();
        }
    });
    
    app.router = AppRouter;
    
})(jQuery, Backbone, _, app);