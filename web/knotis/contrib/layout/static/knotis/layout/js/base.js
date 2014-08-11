;
// Render Forth

(function ($) {
    "use strict";
    
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

    $('.sidebar-nav li').each(function (){
        $(this).hover(function (){
            $(this).css('background', '#3b3b3b');
            $('.sidebar-label').removeClass('sidebar-label-selected');
            $('.sidebar-label').addClass('sidebar-label-selected');
            $(this).find('.sidebar-label-teal').addClass('sidebar-label-selected');
            $('.sidebar-label').css('color', '#363636');
            $(this).find('.circle').css('background', '#363636');
            $('.sidebar-label').addClass('sidebar-label-selected');
        }, function (){
            $(this).css('background', '#fff');
            $(this).find('.circle').css('background', '#595959');
        });
    });

    $('.sidebar-nav li').each(function (){

        $('.sidebar-nav li').css('background', '#fff');

        $(this).click(function (){
            $('.sidebar-nav li').css('background', '#FFF');
            $(this).addClass('sidebar-li-selected');
            
            $(this).each(function (){
                $(this).css('background', '#2cc397');
                $('.sidebar-label').addClass('sidebar-label-selected');
                $('.sidebar-label').addClass('sidebar-label-teal');
            });

            $( "#sidebar-wrapper" ).animate({
                width: "70px",
            },  20, "linear");

            $('.sidebar-overlay').fadeOut(10);

        });
    });

})(jQuery);