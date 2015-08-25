(function($){
    
    
    /*+========================================================================
     *| BINDINGS
     *+======================================================================*/
    // form cancel button
    $('form button[name="btn_cancel"]').on('click', function(){
        var $this = $(this)
          , cancel_url = $this.data('action');
        
        if (!cancel_url) {
            var $form = $this.parentsUntil('form').slice('-1');
            cancel_url = $form.data('cancel');
        };
        window.location = cancel_url;
    });
    
    // table add button
    $('form button[name="btn_add"]').on('click', function() {
       var $this = $(this)
         , addUrl = $this.data('action-url');
       
       if (!addUrl) {
           var $form = $this.parentsUntil('form').slice('-1');
           addUrl = $form.data('add-url');
       };
       window.location = (addUrl || "");
    });
    
})(jQuery);
