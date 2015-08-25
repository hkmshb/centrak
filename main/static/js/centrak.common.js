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
    
})(jQuery);
