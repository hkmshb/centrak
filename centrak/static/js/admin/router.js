(function($, Backbone, _, app) {
    'use strict';
    
    var BaseRouter = Backbone.Router.extend({
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
        }
    }),
    
    
    DefaultRouter = BaseRouter.extend({
        apiservice: function() {
            var view = new app.views.ApiServiceView({el: this.contentElement});
            this.render(view);
        },
    }),
    
    
    AdminXFormRouter = BaseRouter.extend({
        routes: {
            '': 'home',
            ':object_id': 'detail',
        },
        home: function() {
            var view = new app.views.AdminXFormListView({el: this.contentElement});
            this.render(view);
        },
        detail: function(object_id) {
            var view = new app.views.AdminXFormView({
                el: this.contentElement,
                object_id: object_id
            });
            this.render(view);
        }
    }),
    
    RouterFactory = function(rname, vname){
        return {
            r: null,
            map: {
                'adminXform': AdminXFormRouter
            },
            route: function() {
                if (_.isEmpty(rname)) {
                    this.r = new DefaultRouter();
                    this.r[vname]()
                } else {
                    if (!_.isEmpty(this.r))
                        this.r = null;
                    this.r = new this.map[rname]();
                }
            }
        }
    };
    
    app.router = RouterFactory;
    
})(jQuery, Backbone, _, app);