;

(function($) {
    "use strict";

    var Navigation = function () {
    };

    Navigation.address_init = function (force) {
        if (!force && true === this.address_initialized) {
            return false;
        }

        $('a:not([data-dismiss])').address();
        this.address_initialized = true;
        return true;
    };
    
    Navigation.initialize = function () {
        var that = this;

        $("#accordion-nav > li[data-target]").hover(
            function() { 
                target = $(this).data('target');
                $(target).collapse('show') 
            },
            function() { 
                target = $(this).data('target'); 
                $(target).collapse('hide');
            }
        );

        $.address.state('/').change(function (event) {
            if (that.address_init()) {
                return;
            }

            var value = event.value;

            var $clicked_anchor = null;
            // Selects the proper navigation link
            $('.nav a').each(function() {
                if ($(this).attr('href') == value) {
                    $clicked_anchor = $(this);
                    $clicked_anchor.addClass('on').focus();

                } else {
                    $(this).removeClass('on');

                }

            });

            if (null !== $clicked_anchor) {
                var dismiss_modal = $clicked_anchor.attr('data-dismiss');
                if (dismiss_modal !== undefined && dismiss_modal !== false) {
                    return;
                }

                if ($clicked_anchor.hasClass('modal-link')) {
                    var modal_width = $clicked_anchor.attr('data-modal-width');
                    var modal_id = $clicked_anchor.attr('data-modal-id');
                    if (!modal_id) {
                        modal_id = 'modal-box';
                    }
                    $.ajaxmodal({
                        href: $clicked_anchor.attr('href'),
                        modal_width: modal_width,
                        modal_id: modal_id
                    });
                    return;

                }

            }

            $.ajax({
                url: value,
                data: 'format=json',
                complete: function (request, status) {
                    var data = $.parseJSON(request.responseText);
                    if (data.title) {
                        $.address.title(data.title);
                        
                    }

                }
            });

        });

    };

    Navigation.initialize();

})(jQuery);