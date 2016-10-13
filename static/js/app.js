/* jshint laxcomma:true */
var app = (function($){
    var app = {
        "views": {},
        "models": {},
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