/* jshint -W014, laxcomma:true */

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
    app.models.Project = Backbone.Model.extend({
        getFaActive: function() {
            var active = this.get('active');
            return (active? 'fa-check-square-o': 'fa-square-o');
        },
        getDateStarted: function() {
            return this.getDate('date_started');
        },
        getDateEnded: function() {
            return this.getDate('date_ended');
        },
        getDate: function(field_name) {
            var value = this.get(field_name);
            if (!_.isEmpty(value)) {
                if (_.isObject(value))
                    value = value.$date;
                return moment(value).format('DD/MM/YYYY HH:mm A');
            }
            return "";
        },
        getStat: function(stats, statType) {
            var code = this.get('code');
            if (_(stats).has(code))
                return stats[code][statType];
            return 0;
        }
    });
    
    app.models.XForm = Backbone.Model.extend({
        getLastSynced: function() {
            var value = this.get('last_synced');
            if (_.isEmpty(value)) {
                return 'unknown';
            } else {
                if (_.isObject(value))
                    value = value.$date;
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
        },
        getStat: function(stats, statType) {
            var id = this.get('id_string');
            if (_(stats).has(id))
                return stats[id][statType];
            return 0;
        }
    });
    
    app.models.Station = Backbone.Model.extend({
        getFullname: function() {
            var fullname=''
              , n = this.get('name')
              , v = this.get('voltage_ratio');
            
            if (!_.isUndefined(v)) {
                var idx = _(app.voltratio).pluck(0).indexOf(v);
                fullname += (app.voltratio[idx][1] + ' ');
            }
            if (!_.isEmpty(n)) fullname += n;
            return fullname.trim();
        }
    });

    app.models.Office = Backbone.Model.extend({
        getFullAddress: function() {
            var addr_street = this.get('addr_street')
              , addr_town = this.get('addr_town')
              , addr_state = this.get('addr_state')
              , postal_code = this.get('postal_code')
              , addr = addr_street;
            
            if (!_.isNull(addr_street)) {
                if (!_.isEmpty(addr_town)) {
                    if (!_.isEmpty(addr))
                        addr += ', ';
                    addr += addr_town;
                }
            };
            return addr;
        }
    });
    
    
})(jQuery, Backbone, _, app);