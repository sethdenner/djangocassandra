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
                ].join(''),
                modal_id: 'id-redemption-modal',
                modal_width: 845,
                on_open: function(data, status, request) {
                    $('.redemption-form').ajaxform({
                        done: function(data, status, jqxhr) {
                            if (!data.errors) {
                                $('form.redemption-form > input[value=' + data.transaction_context + ']')
                                    .parent()
                                    .parent()
                                    .parent().html(data.message).hide(1000, function(){
                                        $(this).remove();
                                        if (!$('form.redemption-form').length) {
                                            $('#purchases').html('<strong>No redeemable purchases</strong>');
                                        }
                                    });
                            }
                        }
                    });
                }
            });
        });

        $('.toggle-offer').click(function(event){
            var $button = $(this),
                offer_id = $button.parent().parent('.grid-tile.small-tile').attr('data-offer-id'),
                active = $button.text().toLowerCase() == 'resume';
            $.ajax({
                url: '/api/v1/offer/offer/',
                type: 'PUT',
                data: {
                    id: offer_id,
                    active: active
                }
            }).done(function(data, status, jqxhr){
                if (data.errors) return;

                var remove_class = active ? 'btn-success' : 'btn-danger',
                    add_class = active ? 'btn-danger' : 'btn-success';
                $button.removeClass(remove_class).remove_class(add_class)
                    .addClass(add_class)
                    .text(active ? 'Pause' : 'Resume');
            });
        });

        $('.publish-offer').click(function(event){
            var $button = $(this),
                offer_id = $button.parent().parent('.grid-tile.small-tile').attr('data-offer-id');
            $.ajax({
                url: '/api/v1/offer/publish/',
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
