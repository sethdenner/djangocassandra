(function($) {

    var $carousel = $('div#offer-edit-carousel');
    $carousel.carousel({
        interval: false
    });

    var step = function (
        steps,
        index, 
        data
    ) {
        var _step = steps[index];
        var _params = {};
        
        if (!_step) {
            $('#modal-box').modal('hide');
            return;
        }

        if (data) {
            var _stepParams = _step.params;
            for (var key in _stepParams) {
                var _dataKey = _stepParams[key];
                if (_dataKey in data) {
                    _params[key] = data[_dataKey];
                }
            }
        }

        $.get(
            _step.action,
            _params,
            function (data, status, jqxhr) {
                var _container = $(_step.container);
                _container.html(data.html);
                _container.find('form').ajaxform({
                    done: function(data, status, jqxhr) {
                        if (!data.errors) {
                            step(
                                steps,
                                index + 1,
                                data
                            );
                        }
                    }
                });
                $carousel.carousel(index);

            }
        );
        
    };

    step(
        steps,
        0
    );

})(jQuery);