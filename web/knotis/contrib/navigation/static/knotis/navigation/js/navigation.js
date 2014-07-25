;

(function($) {
    "use strict";

    var first_change = true;
    var $clicked_anchor = null;

    var modal_onclose = function () {
        var $close = $(this).find('a[data-dismiss-modal]');
        var href = '/';
        var modal = false;
        var target_id = 'main-content';

        if ($close.length) {
            href = $close.attr('href');
            modal = $close.hasClass('modal-link');
            target_id = $close.attr('data-target-id');

        }

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
        $modals.each(function() {
            var $modal = $(this);
            $modal.modal();
            $modal.on('hidden.bs.modal', modal_onclose);

        });

    };

    var initialize_address = function (force) {
        $('a:not(.no-deep)').off('click.address').on(
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
                        $html.on('hidden.bs.modal', modal_onclose);

                    } else {
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

})(jQuery);