(function($, Backbone, _, app) {
    'use strict';
    
    // CSRF helper functions taken directly from Django docs
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/i.test(method));
    }
    
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Setup jQuery ajax calls to handle CSRF
    $.ajaxPrefilter(function(settings, originalOptions, xhr) {
        var csrftoken;
        if (!csrfSafeMethod(settings.type) && this && !this.crossDomain) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            csrftoken = getCookie('csrftoken');
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
    });
    
    var Session = Backbone.Model.extend({
        defaults: {
            token: null
        },
        initialize: function(options) {
            this.options = options;
            $.ajaxPrefilter($.proxy(this._setupAuth, this));
            this.load();
        },
        load: function() {
            var token = localStorage.apiToken;
            if (token) {
                this.set('token', token);
            }
        },
        save: function(token) {
            this.set('token', token);
            if (token === null) {
                localStorage.removeItem('apiToken');
            } else {
                localStorage.apiToken = token;
            }
        },
        delete: function() {
            this.save(null);
        },
        authenticated: function() {
            return this.get('token') !== null;
        },
        _setupAuth: function(settings, originalOptions, xhr) {
            if (this.authenticated()) {
                xhr.setRequestHeader(
                    'Authorization',
                    'Token' + this.get('token')
                );
            }
        }
    });
    
    
    app.session = new Session();
    app.$fn.getCookie = getCookie;
    
    
    // models
    app.models.XForm = Backbone.Model.extend({
        getLastSynced: function() {
            var value = this.get('last_synced');
            if (_.isEmpty(value)) {
                return 'unknown';
            } else {
                return moment(value).calendar();
            }
        },
        getFaSyncedBy: function() {
            var value = this.get('synced_by');
            if (_.isEmpty(value)) {
                return "fa-question";
            } else if (value === "auto") {
                return "fa-laptop";
            } else {
                return "fa-user";
            }
        },
        getFaActive: function() {
            var active = this.get('active');
            return (active? 'fa-check-square-o': 'fa-square-o');
        }
    });
    
    
    // collections
    // a]. start by discovering the root links published on the api-root
    app.collections.ready = $.getJSON(app.conf.apiRoot);
    
    // b]. build collections using data returned from [a]
    app.collections.ready.done(function(data) {
        // local XForm
        app.collections.XForms = Backbone.Collection.extend({
            model: app.models.XForm,
            url: data.xforms
        });
        app.xforms = new app.collections.XForms();
        
        // survey XForms
        app.collections.SurveyXForms = Backbone.Collection.extend({
            model: app.models.XForm,
            url: app.conf.survey.apiRoot
        })
        app.surveyXforms = new app.collections.SurveyXForms();
        
        /// more collections...
    });
    
    
    // collection extension
    Backbone.Collection.prototype.saveAll = function(data, success){
        var self = this
          , wrapper = {
                url: this.url,
                toJSON: function() {
                    return data;
                }
            },
            options = {
                success: function(model, resp, xhr) {
                    if (success) {
                        success(model, resp, xhr);
                    }
                }
            };
        return Backbone.sync("create", wrapper, options);
    };
    
    
})(jQuery, Backbone, _, app);