;
(function($) {
    $.fn.actionButton = function(options) {
        var settings = $.extend({
            onHover: function($element){},
            onClickResponse: function(data, status, request, $element){}
        }, options);

        return this.each(function(i) {
            var $this = $(this);
            $this.ajaxform({
                'done': function(data, status, request) {
                            settings.onClickResponse(data, status, request, $this);
                        },
                 'method': $this.attr('method').toUpperCase()
            });
        });
    };
})(jQuery);
