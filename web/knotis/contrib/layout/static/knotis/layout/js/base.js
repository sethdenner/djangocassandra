;
// Render Forth

(function ($) {
    "use strict";

    var hideOverlay = function () {
        $('.sidebar-overlay').fadeOut('fast');
        $('.sidebar-label').fadeOut('fast');
        $( "#sidebar-wrapper" ).animate({
            width: "70px",
        },  100, "linear");
    };
    $('html').click(hideOverlay);

    $( ".sideBar" ).hover(function () {
        $( "#sidebar-wrapper" ).animate({
            width: "250px",
        },  100, "linear");

        $('.sidebar-label').fadeIn('fast');
        $('.sidebar-overlay').fadeIn('fast');
    }, function () {
        //
    });

    $('.sidebar-nav li').each(function (){
        $(this).hover(function (){
            $(this).find('.circle').css('background', '#303030');
        }, function (){
            $(this).find('.circle').css('background', '#595959');
        });

    });

})(jQuery);

