(function($, Backbone, _, app) {
    'use strict';
    
    app.collections.XForms = Backbone.Collection.extend({
        model: app.models.XForm,
    });
    
    app.collections.SurveyXForms = Backbone.Collection.extend({
        model: app.models.XForm,
        url: app.conf.survey.apiRoot
    });
    
    app.collections.Stations = Backbone.Collection.extend({
        model: app.models.Station,
    });
    
    app.collections.ready = $.getJSON(app.conf.apiRoot);
    app.collections.ready.done(function(data) {
        // register urls for collections
        app.collections.XForms = app.collections.XForms.extend({
            url: data.xforms,
        });
        app.collections.Stations = app.collections.Stations.extend({
            url: data.pstations,
        });
    
        // create collection instances
        app.xforms = new app.collections.XForms();
        app.surveyXforms = new app.collections.SurveyXForms();
        app.tstations = new app.collections.Stations();
        app.istations = new app.collections.Stations();
    });
    
    
})($, Backbone, _, app);