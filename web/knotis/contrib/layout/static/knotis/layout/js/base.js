// Render Forth

$('.modals').load('views/authModals.html');
$('.nav').load('views/nav.html');
$('.subNav').load('views/subNav.html');
$('.sideBar').load('views/sideBar.html');
$('.offers').load('views/offers.html');
$('.profileBusiness').load('views/profileBusiness.html');

$( ".sideBar" ).hover(
    function() {
        var hideOverlay = $('html').click(function () {
            $('.sidebar-overlay').fadeOut('fast');
            $('.sidebar-label').fadeOut('fast');
            $( "#sidebar-wrapper" ).animate({
                width: "70px",
            },  100, "linear");
        });

        $( "#sidebar-wrapper" ).animate({
            width: "250px",
        },  100, "linear");

        $('.sidebar-label').fadeIn('fast');
        $('.sidebar-overlay').fadeIn('fast');
        hideOverlay();
    },  
    function(){
        //
    });

$('.sidebar-nav li').each(function() {
    $(this).hover(function(){
        $(this).find('.circle').css('background', '#303030');
    }, 
                  function(){
                      $(this).find('.circle').css('background', '#595959');
                  });
});
