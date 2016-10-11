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
                    'Token ' + this.get('token')
                );
            }
        }
    });
    
    
    app.session = new Session();
    app.$hs.getCookie = getCookie;
    app.$hs.auth = {
        initForLogin: function() {
            var data=null, self=this, $form=$('form');
            $form.on('submit', function(e) {
                e.preventDefault();
                data = {
                    username: $('input.username', $form).val(),
                    password: $('input.password', $form).val()
                };
                $.post(app.conf.apiLogin, data)
                 .success($.proxy(self.loginSuccess, this))
                 .fail($.proxy(self.loginFailure, this));
            });
        },
        initForLogout: function() {
            app.session.delete();
        },
        loginSuccess: function(data) {
            app.session.save(data.token);
            this.submit();
        },
        loginFailure: function() {
            this.submit();
        }
    }

})(jQuery, Backbone, _, app);
