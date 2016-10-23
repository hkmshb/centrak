/* jshint -W014, laxcomma: true */

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

    app.$ck = {
        getCookie: getCookie,
        dialog: {
            alert: function(title, message) {
                var f = $('#modal-alert');
                $('.modal-header h3', f).text(title);
                $('.modal-body', f).text(message);
                f.modal({backdrop:'static', keyboard:false, show:true});
            },
            confirm: function(title, message, callback) {
                var f = $('#modal-confirm');
                $('.modal-header h3', f).text(title);
                $('.modal-body', f).text(message);
                f.modal({backdrop:'static', keyboard:false, show:true});

                $('button.yes', f).off('click').on('click', function() {
                    f.modal('hide');
                    callback();
                })
            }
        }
    };

})(jQuery, Backbone, _, app);
