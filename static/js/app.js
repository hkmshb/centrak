/* jshint laxcomma:true */
var app = (function($) {
    var config = $('#config')
      , app = {
            "views": {},
            "models": {},
            "collections": {},
        };

    if (config.length > 0) {
        app.conf = JSON.parse(config.text());
    }

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

    /* chart colours */
    app.colours = {
        green: {norm:'rgb(0,172,127)', lite:'rgba(0,172,172,.2)', dark:'rgba(0,172,172,.9)'},
        orange: {norm:'rgb(243,156,18)', lite:'rgba(243,156,18,.2)', dark:'rgba(243,156,18,.9)'},
        red: {norm:'rgb(221,75,57)', lite:'rgba(221,75,57,.2)', dark:'rgba(221,75,57,.9)'}
    };
    return app;
})(jQuery);