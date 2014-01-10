(function($) {
    $(function(){
        $(window).scroll(function(event) {
            if ($(this).scrollTop() > 550) {
                $('button.btn-to-top').show();
            } else {
                $('button.btn-to-top').hide();
            }
        });

        $('button.btn-to-top').click(function(event) {
            event.preventDefault();
            event.stopPropagation();
            
            var scrollTop = $(window).scrollTop();
            
            $('body').animate({
                    scrollTop: 0,
                }, 500
            );
        });
    });

})(jQuery);