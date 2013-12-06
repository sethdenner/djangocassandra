(function($) {
    $(function() {
        $('form#id-reset-form input#password-input-1').focus();

        $('a#id-forgot-link').click(function(event) {
            event.preventDefault();
            event.stopPropagation();

            $.ajaxmodal({
                href: $(this).attr('href'),
                modal_id: 'auth-modal'
            });
                
        });
    });
})(jQuery);