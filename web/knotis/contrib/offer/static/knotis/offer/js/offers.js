;
(function($) {
    $('.offer-tile').click(function(event) {
        event.preventDefault();

        offer_id = this.getAttribute('data-offer-id');
        $.ajaxmodal({
            href: '/offer/detail/' + offer_id + '/'
        });
    });

})(jQuery);