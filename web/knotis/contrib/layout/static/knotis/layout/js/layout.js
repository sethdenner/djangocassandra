(function($) {

    $('a.modal-link').click(function(event) {
	    event.preventDefault();
        $.ajaxmodal({
            href: this.href
        });
    });

})(jQuery);