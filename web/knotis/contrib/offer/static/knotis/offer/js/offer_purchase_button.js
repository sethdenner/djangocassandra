;
(function($) {
    $(function(){
		$('form#purchase-form').ajaxform({
		    done: function(data, status, jqxhr) {
			    if (data.errors) {
			        alert('There was an error purchasing your offer. Please contact support@knotis.com');
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
		});

	    $('input#purchase-button').click(function(event) {
	        event.preventDefault();
	        event.stopPropagation();
            var quantity = $('select#selectquantity').val();
            $('form#purchase-form input[name=quantity]').val(quantity);
            $('form#purchase-form').submit();
	    });

    });

})(jQuery);
