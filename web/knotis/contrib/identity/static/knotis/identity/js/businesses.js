(function($) {
    $(function(){
        var page = 0;
        var count = 24;
        var results_left = true;
        var fetching_results = false;
        $(window).on('scroll.businesses', function(event) {
            var $this = $(this);

            if (!results_left) {
                $this.off('scroll.businesses');
                return;
            }

            if (!fetching_results && $this.scrollTop() + $this.innerHeight() >= $(document).innerHeight() - 250) {
                fetching_results = true;
                $.get(
                    [
                        '/businesses/grid',
                        ++page,
                        count,
                        ''
                    ].join('/'),
                    function(data, status, request) {
                        data = data.replace(/(\r\n|\n|\r)/gm,"");
                        if (!data) {
                            results_left = false;
                            return;
                        }
                        var $markup = $(data);
                        $markup = $markup.children().children().children();
                        $('.span10.grid > .row-fluid.grid-small > .span12 > .row-fluid').append($markup);
                        fetching_results = false;
                        $.identity.initialize_business_tiles();
                    }
                );
            }
        });
    });
})(jQuery);