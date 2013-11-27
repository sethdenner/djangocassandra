(function($) {
    
    var register_buy_handlers = function() {
        $('button.buy-offer').bind('click.offerBuy', function(event) {
            event.preventDefault();
            event.stopPropagation();

            offer_id = this.getAttribute('data-offer-id');
            window.location = '/offer/' + offer_id + '/buy/';

        });

    };

    register_buy_handlers();

})(jQuery);