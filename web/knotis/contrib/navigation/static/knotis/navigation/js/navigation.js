;

(function($) {
    "use strict";

    var navigation_stack = [];
    var current_navigation = null;
    var next_navigation = null;

    var first_change = true;

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

        next_navigation = {
            address: window.location.pathname,
            anchor: null
        }

    };

    var initialize_address = function (force) {
        $('a:not([data-dismiss-modal])').off('click.address').on(
            'click.address',
            function (event) {
                event.preventDefault();

                var $anchor = $(this);
                var href = $anchor.attr('href');
                next_navigation = {
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

        $('a[data-dismiss-modal]').each(function() {
            $(this).off('click.dismiss').on('click.dismiss', function (event) {
                event.preventDefault();
                var $this = $(this);
                var navigation_item = navigation_stack.pop();
                var dismiss_modal = $this.attr('data-dismiss-modal');
                var autoUpdate = $.address.autoUpdate();
                var histroy = $.address.history();
                $.address.autoUpdate(false);
                $.address.history(false);
                $.address.value(navigation_item.address);
                next_navigation = 'noop';
                $.address.update();
                $.address.history(history);
                $.address.autoUpdate(autoUpdate);
                $('#' + dismiss_modal).modal('hide');

            });

        });

        initialize_address();
    };

    var initialize_navigation = function () {
        initialize_once();
        initialize_always();

        $.address.state('/').change(function (event) {
            if (next_navigation == 'noop') {
                next_navigation = null;
                return;

            }

            var address = event.value;

            if (first_change) {
                // The change event gets triggered in the inital
                // page request. Since the page is already
                // rendered no action is necessary here.
                current_navigation = next_navigation;
                next_navigation = null;
                first_change = false;
                return;

            }

            if (!next_navigation) {
                if (navigation_stack.length) {
                    next_navigation = navigation_stack.pop();

                } else {
                    return;

                }

            }

            var $next_anchor = next_navigation.anchor;
            
            if ($next_anchor.hasClass('modal-link')) {
                var modal_width = $next_anchor.attr('data-modal-width');
                var new_modal_id = $next_anchor.attr('data-modal-id');
                if (modal_id != new_modal_id) {
                    $('#' + modal_id).modal('hide');
                }
                var modal_id = new_modal_id;

                if (!modal_id) {
                    modal_id = 'modal-box';

                }
                $.ajaxmodal({
                    href: $next_anchor.attr('href'),
                    modal_width: modal_width,
                    modal_id: modal_id,
                    on_open: function (data, status, request) {
                        initialize_always();

                    }
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

            var dismiss_modal_attr = $next_anchor.attr('data-dismiss-modal');
            if (typeof dismiss_modal_attr === typeof undefined || dismiss_modal_attr === false) {
                navigation_stack.push(current_navigation);
                current_navigation = next_navigation;

            }
            next_navigation = null;

        });

    };
    
    initialize_navigation();

})(jQuery);