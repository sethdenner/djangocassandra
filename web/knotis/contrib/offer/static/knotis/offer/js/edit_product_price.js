(function($) {

    $('input[name="credit_price"], input[name="credit_value"]').change(function(event){
        var credit_price = parseFloat($('input[name="credit_price"]').val());
        var credit_value = parseFloat($('input[name="credit_value"]').val());

        var discount_percent = 0;
        if (credit_price > 0.0 && credit_value > 0.0) {
            discount_percent = Math.floor(100 - ((credit_price/credit_value) * 100));

        } 

        $('span#discount-percent').text(discount_percent);

        return true;

    });

    $('input#id-physical-product-input').click(function(event) {
        $('div.control-group.physical').show('fast');

        $('input[name="credit_price"], input[name="credit_value"]').prop(
            'disabled',
            true
        );

        $('input[name="product_title"]').prop(
            'disabled',
            false
        );

        $('span#id-offer-discount').hide('fast');

        $('input[name="product_title"]').focus();

        return true;

    });

    $('input#id-credit-product-input').click(function(event) {
        $('div.control-group.physical').hide('fast');

        $('input[name="credit_price"], input[name="credit_value"]').prop(
            'disabled',
            false
        );

        $('input[name="product_title"]').prop(
            'disabled',
            true
        );

        $('span#id-offer-discount').show('fast');

        $('input[name="credit_price"]').focus();
        
        return true;

    });

    $('input#id-unlimited-input').click(function(event) {
        if (this.checked) {
            $('div.control-group.offer-quantity').hide('fast');
            $('input[name="offer_stock"]').prop('disabled', true);

        } else {
            $('div.control-group.offer-quantity').show('fast');
            $('input[name="offer_stock"]').prop('disabled', false);

        }
        return true;

    });

    $('input[name="credit_price"]').focus();
    
})(jQuery);
