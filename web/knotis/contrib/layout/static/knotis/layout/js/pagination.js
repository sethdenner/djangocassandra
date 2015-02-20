;
(function($) {
    $.paginator = function(user_options){
        var options = {
            url:'',
            dataId:'',
            onDone: function() {},
            count_increment: 24,
        };
        $.extend(options, user_options);

        var page = 1;
        var count = options.count_increment;
        var results_left = true;
        var fetching_results = false;
        var scroll_space = 'scroll';

        var get_results = function (page_number) {
            fetching_results = true;
            fetch_url = [
                options.url,
                page,
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

                        return;
                    }

                    var $markup = $(data);
                    $('div[data-id=' + options.dataId + ']').append($markup);

                    fetching_results = false;
                    options.onDone();
                    $.navigation.reinitialize();
                }
            });
        };

        $(window).off(scroll_space).on(scroll_space, function(event) {
            if (page == 1) {

                $('#load_more_button').click(function(event) {
                    $('#knotis_footer').hide();
                    $('#load_more_button').hide();
                    if (!fetching_results) {
                        get_results(page++);
                    }
                });

            } else {
                var $this = $(this);

                if (!results_left) {
                    $this.off(scroll_space);
                    return;
                }

                if (!fetching_results && $this.scrollTop() + $this.innerHeight() >= $(document).innerHeight() - 1000) {
                    get_results(page++);
                }
            }

        });
    };
})(jQuery);
