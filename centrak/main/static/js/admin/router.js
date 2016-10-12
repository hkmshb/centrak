/* jshint laxcomma:true */

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
    
    AdminPowerStationRouter = BaseRouter.extend({
        routes: {
            '': 'home',
            ':type/create': 'create',
        },
        home: function() {
            var view = new app.views.AdminStationListView();
            this.render(view);
        },
        create: function(type) {
            var options = {type: type, el: this.contentElement}
              , view = new app.views.AdminStationFormView(options);
            this.render(view);
        }
    }),
    
    AdminProjectRouter = BaseRouter.extend({
        routes: {
            '': 'home',
            'create': 'create',
            ':project_code/': 'view',
            ':project_code/update': 'update',
        },
        home: function() {
            var view = new app.views.AdminProjectListView({el: this.contentElement});
            this.render(view);
        },
        create: function() {
            this.manage({el: this.contentElement, edit: true});
        },
        view: function(project_code) {
            this.manage({
                el: this.contentElement, 
                project_code: project_code, edit: false
            });
        },
        update: function(project_code) {
            this.manage({
                el: this.contentElement, 
                project_code: project_code, edit: true 
            });
        },
        manage: function(options) {
            var view = new app.views.AdminProjectFormView(options);
            this.render(view);
        }
    }),

    AdminOrgRouter = BaseRouter.extend({
        routes: {
            '': 'home',
            'update': 'update',
        },
        home: function() {
            var view = new app.views.AdminOrgDisplayView({el: this.contentElement});
            this.render(view);
        },
        update: function() {
            var view = new app.views.AdminOrgFormView({
                el: this.contentElement, 
                edit: true
            });
            this.render(view);
        }
    }),
    
    AdminOfficeRouter = BaseRouter.extend({
        routes: {
            '': 'home',
            'create': 'create',
            ':officeId/': 'view',
            ':officeId/update': 'update',
            ':officeId/sp/create': 'createServicePoint',
        },
        home: function() {
            var view = new app.views.AdminOfficeListView({el: this.contentElement});
            this.render(view);
        },
        create: function() {
            this.manage({
                el: this.contentElement, 
                edit: true, isHQ: false
            });
        },
        view: function(officeId) {
            var comp1 = new app.views.AdminOfficeDisplayView({
                            el: this.contentElement,
                            innerEl: '#l-content',
                            itemId: officeId}),
                comp2 = new app.views.AdminServicePointListView({
                            el: this.contentElement,
                            innerEl: '#r-content',
                            parentId: officeId}),
                view  = new app.views.MultiViewManager({
                            comps: {'l': comp1, 'r': comp2}
                        });
            this.render(view);
        },
        update: function(officeId) {
            this.manage({
                urlBack: '#/' + officeId + '/',
                el: this.contentElement,
                itemId: officeId, edit: true
            });
        },
        manage: function(options) {
            var view = new app.views.AdminRegionFormView(options);
            this.render(view);
        },
        createServicePoint: function(officeId) {
            var comp1 = new app.views.AdminOfficeDisplayView({
                            el: this.contentElement,
                            innerEl: '#l-content',
                            itemId: officeId}),
                comp2 = new app.views.AdminServicePointFormView({
                            urlBack: '#/' + officeId + '/',
                            el: this.contentElement,
                            innerEl: '#r-content',
                            parentId: officeId}),
                view  = new app.views.MultiViewManager({
                            comps: {'l': comp1, 'r': comp2}
                        });
            this.render(view);
        }
    }),

    RouterFactory = function(rname, vname){
        return {
            r: null,
            map: {
                'adminXform': AdminXFormRouter,
                'adminPStation': AdminPowerStationRouter,
                'adminProject': AdminProjectRouter,
                'adminOrg': AdminOrgRouter,
                'adminOffices': AdminOfficeRouter,
            },
            route: function() {
                if (_.isEmpty(rname)) {
                    this.r = new DefaultRouter();
                    this.r[vname]();
                } else {
                    if (!_.isEmpty(this.r))
                        this.r = null;
                    this.r = new this.map[rname]();
                }
            }
        };
    };
    
    app.router = RouterFactory;
    
})(jQuery, Backbone, _, app);