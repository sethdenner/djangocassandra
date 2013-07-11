(function($) {

    var $carousel = $('div#offer-edit-carousel');
    var $product_div = $('div#offer-edit-product-form');
    var $details_div = $('div#offer-edit-details-form');
    var $location_div = $('div#offer-edit-location-form');
    var $publish_div = $('div#offer-edit-publish-form');

    $carousel.carousel({
        interval: false
    });

    var step = function(
        uri,
        container,
        number
    ){
        $.get(
            uri,
            {},
            function(data, status, jqxhr) {
                container.html(data.html);
                $carousel.carousel(number);

            }
        );
        
    };

    $.get(
        '/offer/create/product/', 
        {},
        function(data, status, jqxhr) {
            $product_div.html(data.html);
            
            $('form#id-offer-product-price').ajaxform({
                done: function(data, status, jqxhr) {
                    if (!data.errors) {
                        step(
                            '/offer/create/details/?id=' + data.offer_id,
                            $details_div,
                            1
                        );

                    }
                }
                    
            });
        }
    );

})(jQuery);