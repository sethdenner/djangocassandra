(function($) {
    $("#accordion-nav > li[data-target]").hover(
        function() { 
            target = $(this).data('target');
            $(target).collapse('show') 
        },
        function() { 
            target = $(this).data('target'); 
            $(target).collapse('hide');
        }
    );
})(jQuery);