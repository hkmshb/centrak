/* jshint laxcomma:true */

var app = (function($){
    var config = $('#config') 
      , app = {
            "models": {},
            "collections": {},
            "views": {},
            "router": null
        };
    
    if (config.length > 0) {
        app.conf = JSON.parse(config.text());
    }
    
    app.$hs = {
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
                
                $('button.yes', f).on('click', function(){
                    f.modal('hide');
                    callback();
                });
            }
        }
    };
    
    $(document).ready(function(){
        try {
            var $rf = $('.app'), $lk = $('li.logout');

            // removes apiToken on logout
            if (!_.isEmpty($lk)) {
                $lk.on('click', function() {
                    app.$hs.auth.initForLogout();
                });
            }

            // initiates SPA routing...
            app.router =  app.router($rf.data('r'), $rf.data('v'));
            app.router.route();
        } catch (e) {
            // do nothing
        }
    });
    
    return app;
})(jQuery);