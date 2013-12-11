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

    var window_href = window.location.href.replace(/^.*\/\/[^\/]+/, '');
    $('.nav a').each(function(){
        var this_href = this.href.replace(/^.*\/\/[^\/]+/, '');
        if (this_href == window_href) {
            $(this).addClass('on');
        }
    });
})(jQuery);