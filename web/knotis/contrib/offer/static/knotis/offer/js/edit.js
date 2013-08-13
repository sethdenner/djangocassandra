(function($) {

    var $carousel = $('div#offer-edit-carousel');
    $carousel.carousel({
        interval: false
    });

    var steps = [
        { 
            'action': '/offer/create/product/',
            'container': 'div#offer-edit-product-form',
            'params': {}
        },
        { 
            'action': '/offer/create/details/',
            'container': 'div#offer-edit-details-form',
            'params': { 'id': 'offer_id' } 
        },
        { 
            'action': '/offer/create/location/',
            'container': 'div#offer-edit-location-form',
            'params': { 'id': 'offer_id' } 
        },
        { 
            'action': '/offer/create/publish/',
            'container': 'div#offer-edit-publish-form',
            'params': { 'id': 'offer_id' } 
        },
        { 
            'action': '/offer/create/summary/',
            'container': 'div#offer-edit-summary',
            'params': { 'id': 'offer_id' } 
        },
    ];

    var step = function (
        steps,
        index, 
        data
    ) {
        var _step = steps[index];
        var _params = {};
        
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