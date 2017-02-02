/* jshint: laxcomma:true */

(function($, Backbone, _, app) {
    'use strict';

    app.collections.ExternalXForms = Backbone.Collection.extend({
        model: app.models.XForm,
        url: (app.conf && app.conf.survey && app.conf.survey.apiRoot || "")
    });

    app.collections.XForms = Backbone.Collection.extend({
        model: app.models.XForm,
        url: (app.conf && app.conf.xformsEndpoint || "")
    });

    // create collection instances
    app.xforms = new app.collections.XForms();
    app.externalXForms = new app.collections.ExternalXForms();

})(jQuery, Backbone, _, app);