(function($) {

    $(function(){
        var $carousel = $('div#wizard-carousel');
        $carousel.carousel({
            interval: false
        });

        var wizard_name = $carousel.attr('data-wizard-name');

        var step = function (
            index, 
            data
        ) {
            var step_el = $('div#wizard-carousel .item').get(index);

            if (!step_el) {
                $('#modal-box').modal('hide');
                return;
            }

            var _step = {};
            var step_action = step_el.attributes['data-action'].value,
                step_container = step_el.attributes['id'].value,
                wizard_query = $carousel.attr('data-wizard-query');

            $.get(
                step_action,
                wizard_query,
                function (data, status, jqxhr) {
                    if ('success' == status) {
                        var _container = $('div#' + step_container);
                        _container.html(data);
                        _container.find('form').ajaxform({
                            done: function(data, status, jqxhr) {
                                if (!data.errors) {
                                    if (data.wizard_query) {
                                        $carousel.attr(
                                            'data-wizard-query',
                                            data.wizard_query
                                        )
                                    }

                                    step(
                                        index + 1,
                                        data
                                    );
                                }
                            }
                        });
                        _container.find('.wizard-back').click(function(event) {
                            step(index - 1);
                        });
                        $carousel.carousel(index);
                    } else {
                        // error handling 
                    }
                }
            );
        };

        current_step = $carousel.attr('data-current-step');
        if (current_step) {
            step(parseInt(current_step));
        } else {
            step(0);
        }

    });

})(jQuery);
