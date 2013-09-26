(function($) {

    var $carousel = $('div#wizard-carousel');
    $carousel.carousel({
        interval: false
    });

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
        _step.action = step_el.attributes['data-action'].value;
        
        _step.container = step_el.attributes['id'].value;

        var attrs = step_el.attributes;
        var length = attrs.length;
        var param_prefix = "data-param-";
        var param_prefix_length = param_prefix.length;

        var id_map_params = {};
        for( i =0; i < attrs.length; i++) {
            attr = attrs[i]
            if(attr.name.indexOf(param_prefix) == 0) //only ones starting with data-
              id_map_params[attr.name.substr(param_prefix_length)] = attr.value;
        }

        var get_params = {};
        if (data) { 
            for (var key in id_map_params) {
                var _dataKey = id_map_params[key];
                if (_dataKey in data) {
                    get_params[key] = data[_dataKey];
                }
            }
        }

        $.get(
            _step.action,
            get_params,
            function (data, status, jqxhr) {
                if ('success' == status) {
                    var _container = $('div#' + _step.container);
                    _container.html(data);
                    _container.find('form').ajaxform({
                        done: function(data, status, jqxhr) {
                            if (!data.errors) {
                                step(
                                    index + 1,
                                    data
                                );
                            }
                        }
                    });
                    $carousel.carousel(index);
                } else {
                    // error handling 
                }
            }
        );
    };

    step(
        0
    );

})(jQuery);
