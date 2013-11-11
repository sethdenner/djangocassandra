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

            if ($this.scrollTop() + $this.innerHeight() >= $(document).innerHeight()) {
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
                        $('.span10.grid').append(data);
                    }
                );
            }
        });
    });
})(jQuery);