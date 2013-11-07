(function($) {

    $('.modal-link').click(function(event) {
	    event.preventDefault();
        $.ajaxmodal({
            href: $(this).attr('href')
        });
    });

})(jQuery);