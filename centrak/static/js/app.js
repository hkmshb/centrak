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
    
    app.$fn = {
        dialog: {
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
        var router = new app.router();
    });
    
    return app;
})(jQuery);