;
// Render Forth

(function ($) {
    "use strict";

    $( "#sidebar-wrapper" ).delay(1500).hover(function () {
        $( "#sidebar-wrapper" ).animate({
            width: "250px",
        },  200, "linear");

        $('.sidebar-label').fadeIn('fast');
        $('.sidebar-overlay').fadeIn('fast');
    }, function () {
        $( "#sidebar-wrapper" ).animate({
            width: "70px",
        },  20, "linear");
        $('.sidebar-overlay').fadeOut(10);
    });

    $('.sidebar-nav li').each(function (){
        $(this).hover(function (){
            $(this).find('.circle').css('background', '#303030');
        }, function (){
            $(this).find('.circle').css('background', '#595959');
        });

    });

})(jQuery);