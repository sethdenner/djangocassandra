;

(function($){

    $(function(){
        $('.toggle-offer').click(function(event){
            event.stopPropagation();
            event.preventDefault();

            var $button = $(this),
                offer_id = $button.attr('data-offer-id'),
                active = $button.text().toLowerCase() == 'resume';
            $.ajax({
                url: '/api/v0/offer/offer/',
                type: 'PUT',
                data: {
                    id: offer_id,
                    active: active
                }
            }).done(function(data, status, jqxhr){
                if (data.errors) return;

                $button.text(active ? 'Pause' : 'Resume');
            });
        });

        $('.publish-offer').click(function(event){
            var $button = $(this),
                offer_id = $button.parent().parent('.grid-tile.small-tile').attr('data-offer-id');
            $.ajax({
                url: '/api/v0/offer/publish/',
                type: 'PUT',
                data: {
                    offer_id: offer_id,
                    publish_now: true
                }
            }).done(function(data, status, jqxhr){
                if (data.errors) return;

                $button.removeClass('btn-primary').removeClass('btn-success')
                    .addClass('btn-success')
                    .text('Published');
            });
        });

        $('.edit-offer').click(function(event){
            var $button = $(this),
                offer_id = $button.parent().parent('.grid-tile.small-tile').attr('data-offer-id');
            $.ajaxmodal({
                href: [
                    '/offer/create/?id=',
                    offer_id
                ].join(''),
                modal_settings: {
                    backdrop: 'static',
                    keyboard: true
                }
            });
        });
    });

})(jQuery);
