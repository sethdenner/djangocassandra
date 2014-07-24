;

(function($) {
    "use strict";

    var history = [];
    var history_index = null;
    var current_history = null;
    var next_history = null;

    var first_change = true;

    var modal_onclose = function () {

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

        $('div.modal').each(function() {
            var $modal = $(this);
            $modal.modal();
            $modal.on('hidden.bs.modal', modal_onclose);

        });

        var $default_anchor = $('<a></a>');
        $default_anchor.attr('href', window.location.pathname);
        $default_anchor.attr('data-target-id', 'main-content');
        $default_anchor.addClass('defaultAnchor');

        next_history = {
            address: window.location.pathname,
            anchor: $default_anchor
        }

    };

    var initialize_address = function (force) {
        $('a:not(.no-deep)').off('click.address').on(
            'click.address',
            function (event) {
                event.preventDefault();

                var $anchor = $(this);
                var href = $anchor.attr('href');
                next_history = {
                    address: href,
                    anchor: $anchor
                };
                $.address.value(href);

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
            if (next_history == 'noop') {
                next_history = null;
                return;

            }

            var address = event.value;

            if (first_change) {
                // The change event gets triggered in the inital
                // page request. Since the page is already
                // rendered no action is necessary here.
                current_history = next_history;
                next_history = null;
                first_change = false;
                return;

            }

            var back = false;
            var forward = false;
            if (!next_history) {
                if (history.length) {
                    if (
                        history_index >= 1 &&
                        history[history_index - 1].address === address
                    ) {
                        back = true;
                        --history_index;

                    } else if (
                        history_index < history.length - 1 &&
                        history[history_index + 1].address === address
                    ) {
                        forward = true;
                        ++history_index;

                    } else {
                        alert('There was a navigation error :(');

                    }
                    next_history = history[history_index];

                } else {
                    return;

                }

            }

            var current_is_modal = current_history.anchor.hasClass('modal-link');
            var next_is_modal = next_history.anchor.hasClass('modal-link');
            if (current_is_modal && !next_is_modal) {
                $('div.modal').modal('hide');

            }

            var $next_anchor = next_history.anchor;

            var dismiss_modal = false;
            var dismiss_modal_attr = $next_anchor.attr('data-dismiss-modal');
            if (typeof undefined !== typeof dismiss_modal_attr && false !== dismiss_modal_attr) {
                dismiss_modal = true;

            }

            if (!dismiss_modal) {
                if ($next_anchor.hasClass('modal-link')) {
                    var modal_width = $next_anchor.attr('data-modal-width');
                    $.ajaxmodal({
                        href: $next_anchor.attr('href'),
                        modal_width: modal_width,
                        on_open: function (data, status, request) {
                            initialize_always();

                        },
                        on_close: modal_onclose
                    });

                } else {
                    // Hide all modals before rendering this view.
                    var target_element_id = $next_anchor.attr('data-target-id');
                    if (typeof target_element_id === typeof undefined || target_element_id === false) {
                        alert('Anchor element has no "data-target-id" attribute defined!');
                        return;
                    }

                    var $target_element = $('#' + target_element_id);
                    if (!$target_element.length) {
                        alert('Target element #' + target_element_id + 'does not exist in page.');
                        return;
                    }

                    $.ajax({
                        url: address,
                        data: 'format=json',
                        complete: function (request, status) {
                            var data = $.parseJSON(request.responseText);
                            if (data.errors || status === 'error') {
                                alert([
                                    'There was an error processing your request.',
                                    '\n    status: ',
                                    status,,
                                    '\n    response: ',
                                    request.responseText
                                ].join(''));
                                return;
                            }

                            $('div.modal').modal('hide');
                            if (data.title) {
                                $.address.title(data.title);
                                
                            }
                            $target_element.html(data.html);
                            initialize_always();

                        }
                    });
                }
            }

            if (!forward && !back) {
                history.push(current_history);
                history_index = history.length;

            }
            current_history = next_history;
            next_history = null;

        });

    };
    
    initialize_navigation();

})(jQuery);