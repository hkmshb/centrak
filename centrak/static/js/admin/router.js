(function($, Backbone, _, app) {
    'use strict';
    
    var AppRouter = Backbone.Router.extend({
        routes: {
            '': 'apiservice'
        },
        initialize: function(options) {
            this.contentElement = '#apiservice';
            this.current = null;
            Backbone.history.start();
        },
        apiservice: function() {
            var view = new app.views.ApiServiceView({el: this.contentElement});
            this.render(view);
        },
        render: function(view) {
            this.current = view;
        }
    });
    
    app.router = AppRouter;
    
})(jQuery, Backbone, _, app);