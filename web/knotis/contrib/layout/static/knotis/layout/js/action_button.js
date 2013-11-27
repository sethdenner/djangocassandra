(function($) {
    $.fn.actionButton = function(options) {
        var settings = $.extend({
            onHover: function($element){},
            onClickResponse: function(data, status, request, $element){}
        }, options);

        return this.each(function(i) {
            var $this = $(this);
            $this.hover(
                function(event){
                    settings.onHover($this);

                    $this.children('span').show({
                        duration: 50,
                        queue: false
                    }).animate({
                        'opacity': 1
                    }, {
                        duration: 200,
                        queue: false
                    });
                },
                function(event){
                    $('.btn.btn-knotis-action span').animate({
                        'opacity': 0
                    }, {
                        duration: 200,
                        queue: false
                    }).hide({
                        duration: 50,
                        queue: false
                    });
                }
            ).click(
                function(event) {
                    event.preventDefault();
                    event.stopPropagation();

                    var url = $this.attr('href');
                    var method = $this.attr('data-method');
                    var data = {};
                    $.each(this.attributes, function(i, attribute) {
                        if (attribute.name.substring(0, 'data-param-'.length) != 'data-param-') return true;
                        data[attribute.name.replace('data-param-', '').replace('-', '_')] = attribute.value;
                    });

                    if (method == 'get') {
                        data = $.param(data);
                    }

                    $.ajax({
                        url: url,
                        data: data,
                        type: method.toUpperCase(),
                        dataType: 'json'
                    }).done(function(data, status, request) {
                        settings.onClickResponse(data, status, request, $this);

                    }).fail(function(request, status, error) {

                    });
                }
            );
        });
    };
})(jQuery);
