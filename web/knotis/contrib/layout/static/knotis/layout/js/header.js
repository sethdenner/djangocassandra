(function($) {
    $('#support-link').click(function(event) {
        event.stopPropagation();
        event.preventDefault();
        $.ajaxmodal({
            href:'/support/',
            modal_id: 'support-modal'
        });
    });
})(jQuery);
