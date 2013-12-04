(function($) {
    $(function() {
        $('form#id-forgot-form button#id-login-button').click(function(event) {
            event.preventDefault();
            event.stopPropagation();

            $.ajaxmodal({
                href: $(this).attr('href'),
                modal_id: 'auth-modal'
            });
        });
    });
})(jQuery);