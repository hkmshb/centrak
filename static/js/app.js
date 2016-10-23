/* jshint laxcomma:true */
var app = (function($){
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

    return app;
})(jQuery);