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
    
    $(document).ready(function(){
        var router = new app.router();
    });
    
    return app;
})(jQuery);