;
// Render Forth

(function ($) {
    "use strict";

    $(document).ready(function() {
        $('.navbar-toggle').click(function() {

            $( "#sidebar-wrapper").animate({
                width: "250px",
            },  20, "linear");

            $('.sideBar').toggle(function () {
                $('.sidebar-label').fadeIn('fast');
                $('.sidebar-overlay').fadeIn('fast');

                $('.sidebar-nav li').click(function() {
                    $( "#sidebar-wrapper" ).animate({
                        width: "70px",
                    },  20, "linear");
                    $('.sidebar-overlay').fadeOut(10);
                    $('.sideBar').fadeOut(100);
                });
            });
        });
    });

    $( "#sidebar-wrapper").hover(function () {
        $( "#sidebar-wrapper").animate({
            width: "250px",
        },  20, "linear");

        $('.sidebar-label').fadeIn('fast');
        $('.sidebar-overlay').fadeIn('fast');
    }, function () {
        $( "#sidebar-wrapper" ).animate({
            width: "70px",
        },  20, "linear");
        $('.sidebar-overlay').fadeOut(10);
    });

    $('.sidebar-nav li').each(function () {
        $(this).hover(function (){
            $(this).css('background', 'rgb(88, 88, 88)');
            $(this).find('.sidebar-label').css('color', '#ffffff');
        }, function(){
            $(this).css('background', '');
            $(this).find('.sidebar-label').css('color', '');
        });

        $(this).click(function() {

            $( "#sidebar-wrapper" ).animate({
                width: "70px",
            },  20, "linear");
            $('.sidebar-overlay').fadeOut(10);

            $(this).css('background', '');
            $(this).find('.sidebar-label').css('color', '');

            $('.sidebar-nav li').each(function () {
                $(this).removeClass('sidebar-li-selected');
                $(this).find('.sidebar-label').removeClass('sidebar-label-selected');
            });
            $(this).addClass('sidebar-li-selected');
            $(this).find('.sidebar-label').addClass('sidebar-label-selected');
        });
    });

})(jQuery);