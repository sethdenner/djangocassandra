(function($) {
    $(function(){
        var page = 0;
        var count = 20;
        var results_left = true;
        $(window).on('scroll.businesses', function(event) {
            var $this = $(this);

            if (!results_left) {
                $this.off('scroll.businesses');
                return;
            }

            if ($this.scrollTop() + $this.innerHeight() >= $(document).innerHeight() - 250) {
                $.get(
                    [
                        '/search/grid',
                        ++page,
                        count,
                        ''
                    ].join('/'),
                    { 'q': $("#q").val() },
                    function(data, status, request) {
                        data = data.replace(/(\r\n|\n|\r)/gm,"");
                        if (!data) {
                            results_left = false;
                            return;
                        }
                        var $markup = $(data);
                        $markup = $markup.children().children().children();
                        $('.span10.grid > .row-fluid.grid-small > .span12 > .row-fluid').append($markup);
                    }
                );
            }
        });
    });
})(jQuery);
