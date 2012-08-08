$(document).ready(function() {

    var server = "http://localhost:8888/knotis/webapp/index.php/";

    // Popup in home with all the places
    $('#makeknotisyours').live('click', function() {
        $('.log_in_popup').remove();

        $.post([server + "home/popup_places"].join('/'), {},

                function(data) {

                    $(".column-map").append(data);

                });


    });


    // Popup that load the view login
    $('.log_in').live('click', function() {

        $('.signup_popup').remove();

        $.post([server + "user/log_in_popup"].join('/'), {},

                function(data) {

                    $(".header-content").append(data).fadeIn;


                });
    });

    $('.play').live('mouseover', function() {
        var cont = $(this).attr("data-play")
        $(".play" + cont).show();

    });

    $('.play').live('mouseout', function() {
        $(".playtooltip").hide();

    });

    $('.pause').live('mouseover', function() {
        var cont = $(this).attr("data-pause")
        $(".stop" + cont).show();

    });

    $('.pause').live('mouseout', function() {
        $(".pausetooltip").hide();

    });


    // Popup that load the view signin
    $('.arrow-user').live('mouseover', function() {
        $(".option-user").show();

    });


    // Popup that load the view signin
    $('.sig_in').live('click', function() {
        $.post([server + "user/sign_up_popup"].join('/'), {},
                function(data) {
                    $(".header-content").append(data).fadeIn;
                });

    });


    $('.close_sig_in').live('click', function() {
        $('.signup_popup').remove().fadeOut;
    });

    $('.close_log_in').live('click', function() {
        $('.log_in_popup').remove().fadeOut;
    });

    // Functions for jquery calendar

    $("#startdate").datepicker({ dateFormat: 'yy-mm-dd' });
    $("#enddate").datepicker({ dateFormat: 'yy-mm-dd' });

    // Jquery Uniform
    $("input:checkbox, input:file, textarea, select").uniform();


    // For categories in the deals page

    $('.categories-filter').live('click', function() {
        var $this = $(this),
                filters = $('.categories-filter'),
                filter = $this.attr('data-filter'),
                categoryname = $this.attr('data-category_name'),
                $category = $('.' + categoryname),
                id = $(this).attr('data-category');


        $.post([server + "deals/deals_list", filter, id].join('/'), {}, function(data) {
            $('.deal-content').replaceWith(data);
            $('.relative a').removeClass('active');
            $('.arrow').remove();
            $('.' + categoryname + ' a').addClass('active');
            $('.' + categoryname).append('<div class="arrow arrow-' + categoryname + '"></div>');
        });


    });


    $('.deallist_backend li a').live('click', function() {
        var $this = $(this),
            filter = $this.attr('data-filter');


        $.post([server + "backend/deals_list", filter].join('/'), {}, function(data) {
            $('.deal_list_backend').replaceWith(data);
            $('.deallist_backend li a').removeClass('active');
            $this.addClass('active');
        });


    });


    $('.playstop').live('click', function() {

        var $this = $(this),
                status = $this.attr('data-status'),
                id = $this.attr('data-id');

        $.post([server + "backend/status", status,id].join('/'), {},

                function(data) {

                    $('.notify').fadeOut();
                });

        $this.fadeOut();


    });


      $('.playstop').live('event', function() {

        var $this = $(this),
                status = $this.attr('data-status'),
                id = $this.attr('data-id');

        $.post([server + "backend/status", status,id].join('/'), {},

                function(data) {

                    $('.notify').fadeOut();
                });

        $this.fadeOut();


    });


    $('.notify').live('click', function() {


        $.post([server + "user/notify_me"].join('/'), {},

                function(data) {

            $('.notify').fadeOut();
        });


    });

    $('.delete-image').live('click', function() {

        var $this = $(this),
                id = $this.attr('data-id'),
                cont = $this.attr('data-cont');

        $.post([server + "backend/delete_image",id].join('/'), {},

                function(data) {

            $('.'+cont).fadeOut();
        });


    });


    // Button follow in business profile
    $('.followme').live('click', function() {

        var $this = $(this),
                id = $this.attr('data-id');

        $.post([server + "business/follow_me",id].join('/'), {},

                function(data) {

            $this.fadeOut();
        });


    });

        // Button follow in business profile
    $('.unfollowme').live('click', function() {

        var $this = $(this),
                idFollow = $this.attr('data-idFollow');

        $.post([server + "business/unfollow_me",idFollow].join('/'), {},

                function(data) {

            $this.fadeOut();
        });


    });

           // Button follow in business profile
    $('.headimage').live('click', function() {

        var $this = $(this),
            id = $this.attr('data-id');

        $.post([server + "backend/headimage",id].join('/'), {},

                function(data) {

            $this.removeClass('active');
        });


    });


    $('.noheadimage').live('click', function() {

        var $this = $(this),
            id = $this.attr('data-id');

        $.post([server + "backend/noheadimage",id].join('/'), {},

                function(data) {

            $this.addClass('active');
        });


    });
        

    // slider images business profile

    $('#controller a').click(function(e) {
        e.preventDefault();
        clearInterval(intervalgallery);
        $('#controller a').removeClass('selected');
        $(this).addClass('selected');
        var imgIndex = $(this).attr('href').substr(1);
        $('#rotator img.active').fadeOut("normal", function () {
            $(this).removeClass('active');
            $('#rotator img:eq(' + imgIndex + ')').fadeIn('slow').addClass('active');
        });
        intervalgallery = setInterval("showImg()", 5000);
    });


});

function showImg() {
    var imgActive = $('#rotator img.active');
    $('#controller a').removeClass('selected');
    $('#rotator img.active').fadeOut("normal", function () {
        if($(this).next('img').attr('src')) {
            $(this).removeClass('active');
            $(this).next('img').fadeIn('slow').addClass('active');
            $("#rotator img").each(function(i, item) {
                if ($(item).hasClass("active")) {
                    $('#controller a:eq('+(i)+')').addClass('selected');
                    return false;
                }
            });
        }
        else {
            $(this).removeClass('active');
            $('#rotator img:first').fadeIn('slow').addClass('active');
            $('#controller a:first').addClass('selected');
        }
    });
}
var intervalgallery = setInterval("showImg()",10000);






