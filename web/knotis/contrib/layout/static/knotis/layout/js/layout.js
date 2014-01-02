(function($) {

    $('.modal-link').click(function(event) {
	    event.preventDefault();

        var modal_width = $(this).attr('data-modal-width');
        var modal_id = $(this).attr('data-modal-id');
        if (!modal_id) {
            modal_id = 'modal-box';
        }
        $.ajaxmodal({
            href: $(this).attr('href'),
            modal_width: modal_width,
            modal_id: modal_id
        });
    });

})(jQuery);