;
(function($) {
    $('.offer-tile').click(function(event) {
        event.preventDefault();

        offer_id = this.getAttribute('data-offer-id');
        $.ajaxmodal({
            href: '/offer/detail/' + offer_id + '/',
            modal_id: 'id-offer-detail',
            modal_width: '750px'
        });
    });

    var open_offer_id = $('input#open_offer_id').val();
    if (open_offer_id) {
        $.ajaxmodal({
            href: '/offer/detail/' + open_offer_id + '/',
            modal_id: 'id-offer-detail',
            modal_width: '750px'
        });
    }

})(jQuery);