;
(function($) {
    $(function(){
	$('select#selectquantity').change(function(event) {
	    var quantity = $(this).val();
	    var total = $('input#item-price').val() * quantity;

	    $('input#total-price').val(total);
	    $('span#total-price-display').text(total);
	});
    });

})(jQuery);
