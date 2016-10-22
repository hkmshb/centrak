/* jshint laxcomma:true */
var app = (function($){
    var config = $('#config')
      , app = {
            "views": {},
            "models": {},
        };

    if (config.length > 0) {
        app.conf = JSON.parse(config.text());
    }

    app.$ck = {
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

    $(document).ready(function() {
        var $hook = $('.hook')
          , name = null;

        if (!_.isEmpty($hook)) {
            name = $hook.data('v');
            if (!_.isEmpty(name)) {
                var view = app.views[name]
                    instance = null;

                if (!_.isEmpty(view)) {
                    instance = new view();
                    instance.render();
                }
            }
        }
    });

    return app;
})(jQuery);