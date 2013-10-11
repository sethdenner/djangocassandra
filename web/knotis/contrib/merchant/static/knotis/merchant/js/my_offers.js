;

(function($){

    $(function(){
        $('.redeem-offer').click(function(event){
            event.preventDefault();
            
            var offer_id = $(this).parent().parent('.grid-tile.small-tile').attr('data-offer-id');
            $.ajaxmodal({
                href: [
                    '/my/offers/redeem/',
                    offer_id,
                    '/'
                ].join('')
            });
        });
    });
    
})(jQuery);