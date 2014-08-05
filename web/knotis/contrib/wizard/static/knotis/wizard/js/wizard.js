(function($) {
    var _init = function(wizard, options) {
        var settings = $.extend({
            modal_id: 'modal-box',
            step_callback: function(index){}
        }, options);

        console.log(this);

        var $carousel = $(wizard);
        $carousel.carousel({
            interval: false
        });

        current_step = $carousel.attr('data-current-step');
        if (current_step) {
            $carousel.wizard('step', {
                index: parseInt(current_step),
                callback: settings.step_callback,
                modal_id: settings.modal_id
            });

        } else {
            $carousel.wizard('step', {
                index: 0,
                callback: settings.step_callback,
                modal_id: settings.modal_id
            });
        }
    };

    var _step = function(wizard, options) {
        var settings = $.extend({
            index: 0,
            callback: function(index){},
            modal_id: 'modal-box'
        }, options);

        var $carousel = $(wizard),
        step_el = $carousel.find('.item').get(settings.index);

        console.log(step_el);
        if (!step_el) {
            $('#' + settings.modal_id).modal('hide');
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

                                $carousel.wizard('step', {
                                    index: settings.index + 1,
                                    callback: settings.callback,
                                    modal_id: settings.modal_id
                                });
                            }
                        }
                    });

                    _container.find('.wizard-back').click(function(event) {
                        $carousel.wizard('step', {
                            index: settings.index - 1,
                            callback: settings.callback,
                            modal_id: settings.modal_id
                        });
                    });

                    $carousel.carousel(settings.index);
                    $carousel.attr('data-current-step', settings.index);
                    
                    if (settings.callback) {
                        settings.callback(settings.index);
                    }
                } else {
                    // error handling 
                }
            }
        );
    };

    $.fn.wizard = function(method, options) {
        if ('init' == method) {
            this.each(function(index, element) {
                _init(element, options);
            });

        } else if ('step' == method) {
            this.each(function(index, element) {
                _step(element, options);
            });
        }
    };

    $.wizard = {
        step: _step
    };

})(jQuery);
