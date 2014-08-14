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

        $(window).on('scroll.businesses', function(event) {

            var $this = $(this);

            $businesses = $('.contentBlock > .businesses')
            if (!$businesses.length || !results_left) {
                $this.off('scroll.businesses');
                return;
            }

            if (!fetching_results && $this.scrollTop() + $this.innerHeight() >= $(document).innerHeight() - 1000) {
                fetching_results = true;
                fetch_url = [
                        '/businesses/grid',
                        ++page,
                        count,
                        ''
                    ].join('/');
                $.ajax({
                    url: fetch_url,
                    global: false,
                    success: function(data, status, request) {
                        data = data.replace(/(\r\n|\n|\r)/gm,"");
                        if (!data) {
                            results_left = false;
                            /*
                            $('.span10.grid > .row-fluid.grid-small > .span12 > .row-fluid').after(
                                no_more_markup
                            );
                            */
                            return;
                        }
                        var $markup = $(data);
                        $markup = $markup.children().children().children();
                        $('.span12 > .row-fluid').append($markup);
                        /*
                        if (0 === page % auto_paging_cutoff) {
                            $('.span10.grid > .row-fluid.grid-small > .span12 > .row-fluid').after(
                                load_more_markup
                            );
                            $('button.btn-load-more').click(function(event) {
                                $(this).parent().remove();
                                fetching_results = false;
                                $(window).scroll();
                            });

                        } else {
                        }
                        */
                        fetching_results = false;
                        $.identity.initialize_business_tiles();
                    }
                });
            }
        });
    });
})(jQuery);
