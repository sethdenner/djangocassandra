;
(function($) {
    $(function(){

        var page = 0;
        var count = 24;
        var auto_paging_cutoff = 3;
        var results_left = true;
        var fetching_results = false;
        var load_more_markup =  '<div class="row-fluid load-more">' +
            '<button class="btn btn-knotis-action btn-load-more">Load More Results</button>' +
            '</div>'
        var no_more_markup = '<div class="row-fluid load-more">' +
            '<button disabled class="btn btn-knotis-action btn-load-more">No More Results</button>' +
            '</div>'

        $(window).on('scroll.offers', function(event) {

            var $this = $(this);

            $offers = $('.contentBlock > .offers')

            if (!$offers.length || !results_left) {
                $this.off('scroll.offers');
                return;
            }

            if (!fetching_results && $this.scrollTop() + $this.innerHeight() >= $(document).innerHeight() - 1000) {
                fetching_results = true;
                fetch_url = [
                        '/offer/grid',
                        ++page,
                        count,
                        ''
                    ].join('/');
                $.get(
                    fetch_url,
                    function(data, status, request) {
                        data = data.replace(/(\r\n|\n|\r)/gm,"");
                        if (!data) {
                            results_left = false;
                            return;
                        }

                        var $markup = $(data);
                        $markup = $markup.children().children().children();

                        $('.span12 > .row-fluid').append($markup);
                        fetching_results = false;
                    }
                );
            }
        });
    });

})(jQuery);
