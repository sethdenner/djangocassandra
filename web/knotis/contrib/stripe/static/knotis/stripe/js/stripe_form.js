;
(function($) {
    var stripeHandler = null,
    configureStripe = function () {
        if ('undefined' === typeof StripeCheckout) {
            window.setTimeout(function() { configureStripe(); }, 50);
            return;

        }

	    stripeHandler = StripeCheckout.configure({
	        key: $('input[name="stripe_api_key"]').val(),
	        image: $('input[name="business_badge"]').val(),
	        token: function(token, args) {
		        var amount = $('input#total-price').val();
		        var offerId = $('input#offerId').val();
		        var transaction_context = $('input#transaction_context').val();
		        var quantity = $('select#selectquantity').val();
		        $('form#stripe-form').append(
		            $(
			            '<input type="hidden" name="stripeToken" value="' +
			                token.id +
			                '" />'
		            )
		        ).append(
		            $(
			            '<input type="hidden" name="chargeAmount" value="' +
			                amount +
			                '" />'
		            )
		        ).append(
		            $(
			            '<input type="hidden" name="quantity" value="' +
			                quantity +
			                '" />'
		            )
		        ).ajaxform({
		            done: function(data, status, jqxhr) {
			            if (data.errors) {
			                alert('There was an error making your payment. Please contact support@knotis.com');
			            } else {
			                $.ajaxmodal({
				                href: './success/',
				                modal_id: 'payment-success'
			                });

			                setTimeout(function(){
				                window.location = '/my/purchases/'
			                }, 4000);
			                
			            }
		            }
		        }).submit();
	        },

	    });
    };

    var onReady = function () {
        configureStripe();

	    $('input#stripe-button').click(function(event) {
	        event.preventDefault();
	        event.stopPropagation();

	        stripeHandler.open({
		        name: $('input[name="business_name"]').val(),
		        description: $('input[name="description"]').val(),
		        ammount: $('input[name="offer_price"]').val()
	        });

	    });
    };
    
    if ($.isReady) {
        onReady();

    } else {
        $(function(){
            onReady();
        });

    }

})(jQuery);
