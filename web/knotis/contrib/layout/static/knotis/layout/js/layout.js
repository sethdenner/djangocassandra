(function($) {

    $('a.modal-link').click(function(event) {
	    event.preventDefault();
	    $('#modal-box').modal();

	    $.get(
	        this.href,
	        {},
	        function(data, status, jqxhr) {
		        $('#modal-box').html(data);
	        }
	    );
    });

})(jQuery);