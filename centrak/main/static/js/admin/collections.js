(function($, Backbone, _, app) {
    'use strict';
    
    
    app.collections.SurveyXForms = Backbone.Collection.extend({
        model: app.models.XForm,
        url: app.conf.survey.apiRoot
    });
    
    app.collections.ready = $.getJSON(app.conf.apiRoot);
    app.collections.ready.done(function(data) {
        
        // register urls for collections
        app.collections.Projects = Backbone.Collection.extend({
            model: app.models.Project,
            url: data.projects,
        });
        
        app.collections.XForms = Backbone.Collection.extend({
            model: app.models.XForm,
            url: data.xforms,
        });
        
        app.collections.Stations = Backbone.Collection.extend({
            model: app.models.Station,
            url: data.stations,
        });

        app.collections.Organizations = Backbone.Collection.extend({
            model: app.models.Organization,
            url: data.organizations,
        })

        app.collections.Offices = Backbone.Collection.extend({
            model: app.models.Office,
            url: data.offices,
        });
        
        // create collection instances
        app.xforms = new app.collections.XForms();
        app.projects = new app.collections.Projects();
        app.surveyXforms = new app.collections.SurveyXForms();
        app.tstations = new app.collections.Stations();
        app.istations = new app.collections.Stations();
        app.organizations = new app.collections.Organizations();
        app.offices = new app.collections.Offices();
    });
    
    
})($, Backbone, _, app);