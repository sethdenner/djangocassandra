;
// Render Forth

(function ($) {
    "use strict";

    $( "#sidebar-wrapper" ).hover(function () {
        $( "#sidebar-wrapper" ).animate({
            width: "250px",
        },  100, "linear");

        $('.sidebar-label').fadeIn('fast');
        $('.sidebar-overlay').fadeIn('fast');
    }, function () {
        $( "#sidebar-wrapper" ).animate({
            width: "75px",
        },  100, "linear");
        $('.sidebar-overlay').fadeOut('fast');
    });

    $('.sidebar-nav li').each(function (){
        $(this).hover(function (){
            $(this).find('.circle').css('background', '#303030');
        }, function (){
            $(this).find('.circle').css('background', '#595959');
        });

    });

})(jQuery);

