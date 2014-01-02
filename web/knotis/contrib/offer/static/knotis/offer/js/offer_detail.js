(function($) {
    $(function(){
        $('#id-offer-detail .business-name').click(function(event){
            event.preventDefault();
            event.stopPropagation();
            
            var business_id = $(this).attr('data-business-id');
            window.location = '/id/' + business_id;
        });
    });

})(jQuery);