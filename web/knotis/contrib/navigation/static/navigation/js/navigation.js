(function($) {
    $("#accordian-nav > li[data-target]").parent('li').hover(
        function() { 
            target = $(this).children('li[data-target]').data('target');
            $(target).collapse('show') 
        },
        function() { 
            target = $(this).children('li[data-target]').data('target'); 
            $(target).collapse('hide');
        }
    );
})(jQuery);