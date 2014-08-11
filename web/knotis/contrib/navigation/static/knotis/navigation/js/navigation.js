;

(function($) {
    "use strict";

    var first_change = true;
    var closing_modal = false;
    var $clicked_anchor = null;
    var last_non_modal = null;

    var modal_onclose = function () {
        var $modal = $(this);
        var $close = $modal.find('a[data-dismiss-modal]');
        var href = '/';

        if (null !== last_non_modal) {
            href = last_non_modal;

        } else if ($close.length) {
            href = $close.attr('href');

        }

        closing_modal = true;
        $.address.value(href);

    };

    var initialize_once = function () {
        $('#accordion-nav > li[data-target]').hover(
            function () { 
                target = $(this).data('target');
                $(target).collapse('show') 

            },
            function () { 
                target = $(this).data('target'); 
                $(target).collapse('hide');

            }
        );

        var $modals = $('div.modal');
        $modals.each(function () {
            var $modal = $(this);
            $modal.modal();
            $modal.off('hidden.bs.modal.navigation')
                .on(
                    'hidden.bs.modal.navigation',
                    modal_onclose
                );

        });

        if (0 === $('div.modal:visible').length) {
            last_non_modal = $.address.value();

        }
    };

    var initialize_address = function (force) {
        $('a:not(.no-deep):not([target="_blank"]').off('click.address').on(
            'click.address',
            function (event) {
                event.preventDefault();

                $clicked_anchor = $(this);
                $.address.value($clicked_anchor.attr('href'));

            }
        );
    };
    
    var initialize_always = function (address) {
        if (!address) {
            address = window.location.pathname;

        }

        // Style links that point to the current page appropriately.
        $('.nav a').each(function() {
            if ($(this).attr('href') === address) {
                $(this).addClass('on').focus();

            } else {
                $(this).removeClass('on');

            }
        });

        initialize_address();
    };

    var initialize_navigation = function () {
        initialize_once();
        initialize_always();

        $.address.state('/').change(function (event) {
            var address = event.value;

            if (first_change) {
                // The change event gets triggered in the inital
                // page request. Since the page is already
                // rendered no action is necessary here.
                first_change = false;
                return;

            }

            if (closing_modal) {
                closing_modal = false;
                return;

            }

            $.ajax({
                url: address,
                data: 'format=json',
                complete: function (request, status) {
                    var data = $.parseJSON(request.responseText);
                    if (status === 'error') {
                        alert([
                            'There was an error processing your request.',
                            '\n    status: ',
                            status,
                            '\n    response: ',
                            request.responseText
                        ].join(''));
                        return;
                    }
                    var $html = $(data.html);

                    if (typeof undefined !== typeof data.modal) {
                        var $existing_modal = $('#' + $html.attr('id'));
                        if ($existing_modal.length) {
                            $existing_modal.html($html.html());
                            $html = $existing_modal;

                        } else {
                            $('body').append($html);

                        }

                        $html.modal();
                        $html.off('hidden.bs.modal.navigation')
                            .on('hidden.bs.modal.navigation', modal_onclose);

                    } else {
                        last_non_modal = address;

                        var target_id = data.targetid;
                        if (!target_id) {
                            alert('View needs to set a data.targetid!');
                            return;
                        }

                        var $target_element = $('#' + target_id);
                        if (0 === $target_element.length) {
                            alert('Target element #' + target_id + ' not found in DOM.');
                            return;
                        }

                        if (data.title) {
                            $.address.title(data.title);
                            
                        }
                        $target_element.html(data.html);
                        $('div.modal').modal('hide');

                    }
                    initialize_always();

                }
            });

            $clicked_anchor = null;
        });

    };
    
    initialize_navigation();

    $(window).on('beforeunload', function () {
        $.loading('on');

    });

})(jQuery);