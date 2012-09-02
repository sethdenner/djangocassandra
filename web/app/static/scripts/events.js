//ONLY FOR DEVELOPER TIME

if (location.hostname == 'localhost') {
    var server = "/knotis/webapp/";
}

else {
    var server = "/";
}

var login = 0;

//

$(document).ready(function() {

    //set up validaty
    $.validity.setup({
        scrollTo: true    
    });
   
      
    // private vars
    var facebookAppId = $('#fb-root').attr('data-app-id');

    // Ajax loading

    $("#ajaxBusy").ajaxStart(function() {
        $(this).show();
    });
    $("#ajaxBusy").ajaxStop(function() {
        $(this).hide();
    });


    // Disable some of the non-functional feature links
    $('a.happy, a.events, a.coming-soon').click(function(e) {
        e.preventDefault();
    });

    // Popup in home with all the places
    $('#makeknotisyours').live('mouseover', function() {
        $('.log_in_popup').remove();

        $.post([server + "home/popup_places"].join('/'), {},

                function(data) {

                    $(".column-map").append(data);

                });
        return false;

    });



    // Popup that load the view signin
    $('.load_conditions').live('click', function() {

        $('.signup_popup').remove();

        $('.log_in_popup').remove();


        $.post([server + "user/conditions"].join('/'), {},

                function(data) {
                    $("input:checkbox").uniform();


                    $(".header-content").append(data).fadeIn;

                    $("#login").validity(function() {

                        $("#email")// The first input:
                                .require();// Required:

                        $("#password").require();


                    });

                    $("input:text").placeholder();


                });
        return false;

    });

    // Popup that load the view signin
    $('.arrow-user').live('mouseover', function() {

        $('.option-user').show();

        return false;

    });

    var ua = navigator.userAgent,
            event = (ua.match(/iPad/i)) ? "touchstart" : "click";

    $('.arrow-user').bind(event, function(e) {
        $('.option-user').show();

        return false;
    });


    // error message close

    $('.close-message').live('click', function() {
        $('.closeinfo').fadeOut();
        return false;

    });

    // Popup that load the view login
    $('.log_in').live('click', function() {
        $('.signup_popup').remove();
        $('.log_in_popup').remove();

        $.get('/auth/login/', {},
                function(data) {
                    $("input:checkbox").uniform();
                    $(".header-content").append(data).fadeIn;
                    $("#login").validity(function() {
                        $("#email")// The first input:
                                .require();// Required:
                        $("#password").require();
                    });
                    $("input:text").placeholder();
                });
        return false;
    });
    
    auto_login = $('#auto_login');
    if (auto_login.length != 0) {
        $('.log_in').click();
    }

    // Popup that load the view login
    $('.signup_pop').live('click', function() {

        var $this = $(this), type = $this.attr('data-type');

        if (type == 'user')
            $("#fb-root").attr('data-sign-up-action', server + "user/facebook_login/1");
        if (type == 'foreverfree')
            $("#fb-root").attr('data-sign-up-action', server + "user/facebook_login/2");
        if (type == 'premium')
            $("#fb-root").attr('data-sign-up-action', server + "user/facebook_login/3");


        $('.signup_popup').remove();

        $('.log_in_popup').remove();

        $.get("/signup/" + type, {},

                function(data) {

                    $(".header-content").append(data).fadeIn;

                    $("input:text").placeholder();

                    $("input:textarea, select, input:radio").uniform();

                    $("#newuser").validity(function() {

                        $("#email")// The first input:
                                .require();// Required:
                        $("#password")// The first input:
                                .require();// Required:

                    });

                });


        return false;
    });


    $("#search").keyup(function(event) {
        if (event.keyCode == 13) {
            var string = $("#search").val();
            window.location = server +"deals/keywords/" + string;
        }
    });

    // count characters

    $("#title_deal").charCount({
        allowed: 50,
        warning: 20
    });


    $('.header-bottom').live('mouseover', function() {
        $(".content-popup-header").hide();
        $(".option-user").hide();

    });

    $('.btn-header-location').live('mouseover', function() {
        $(".content-popup-header").show();

    });

    $('#content').live('mouseover', function() {
        $(".content-popup-header").hide();
        $(".option-user").hide();

    });


    $('.close_sig_in').live('click', function() {
        $('.signup_popup').remove().fadeOut;
    });

    $('.close_log_in').live('click', function() {
        $('.log_in_popup').remove().fadeOut;
        login = 0;
    });

    // Functions for jquery calendar

    $("#startdate").datetimepicker({
        timeFormat: 'hh:mm:ss',
        separator: '  ',
        dateFormat: 'mm/dd/yy'


    });

//    $("input:text").placeholder();
    
    $("#enddate").datetimepicker({
        timeFormat: 'hh:mm:ss',
        separator: '  ',
        dateFormat: 'mm/dd/yy'
    });

    // Jquery Uniform
    $("input:checkbox, textarea, select, input:radio").uniform();


    // For categories in the deals page

    $('.categories-filter').live('click', function() {
        var $this = $(this),
                filters = $('.categories-filter'),
                filter = $('.deal-data').attr('data-filter'),
                cityId = $('.deal-data').attr('data-cityId'),
                neightbourhoodId = $('.deal-data').attr('data-neightbourhoodId'),
                categoryname = $this.attr('data-category_name'),
                $category = $('.' + categoryname),
                id = $(this).attr('data-category');

        $.post([server + "deals/deals_list",cityId,neightbourhoodId, filter, id].join('/'), {}, function(data) {
            $('.more-results').remove();

            $('.deal-content').replaceWith(data);
            $('.list-backend .relative a').removeClass('active');
            $('.arrow').remove();
            $('.mode-map a').removeClass('active');
            $('.mode-list a').addClass('active');
            $('.' + categoryname + ' a').addClass('active');
            $('.' + categoryname).append('<div class="arrow arrow-' + categoryname + '"></div>');


        });


        return false;

    });


// For nodes maps

    $('.deal-mode-map').live('click', function() {
        var $this = $(this),
                filter = $('.deal-data').attr('data-filter'),
                cityId = $('.deal-data').attr('data-cityId'),
                neightbourhoodId = $('.deal-data').attr('data-neightbourhoodId'),
                id = $('.deal-data').attr('data-id');

        $.post([server + "deals/deals_list_map", cityId, neightbourhoodId, filter, id].join('/'), {}, function(data) {
            $('.deal-data').replaceWith(data);
            $('.mode-map a').addClass('active');
            $('.mode-list a').removeClass('active');
        });

        return false;

    });


    $('#price_deal_input').keyup(function () {

        var value = $("#price_deal_input").val();
        $('#price_deal_radio').replaceWith('<p id="price_deal_radio" class="left label-new price_deal_radio">' + value + '</p>');
        $('#price_deal_radio2').replaceWith('<p id="price_deal_radio2" class="left label-new price_deal_radio">' + value + '</p>');

    });

    $('#old_deal_input').keyup(function () {

        var value = $("#old_deal_input").val();
        $('#old_deal_radio').replaceWith('<p id="old_deal_radio" class="left label-new">' + value + '</p>');
        $('#old_deal_radio2').replaceWith('<p id="old_deal_radio2" class="left label-new">' + value + '</p>');

        var value_new = $("#price_deal_input").val();


    });

    var updateDiscount = function(){
        var value = $("#old_deal_input").val();

        var value_new = $("#price_deal_input").val();

        var discount = value - value_new;
        
        if (0 >= discount) {
            $('.discount_val').addClass('discount_error')
                .html('Discount price must be less than retail price!');
            return;
        }
        
        var percent = (discount * 100) / value;

        $('.discount_val').removeClass('discount_error')
            .html('Customers will recieve a discount of <strong>$' + 
                discount + 
                '</strong> on a purchase of <strong>$' +
                value +
                '</strong>. (customers save %' +
                percent.toFixed() +
                ')');
    };
    
    $('#price_deal_input').change(updateDiscount).keyup(updateDiscount);
    $('#old_deal_input').change(updateDiscount).keyup(updateDiscount);
    updateDiscount();

    $('#title_deal_input').keyup(function () {
        var value = $("#title_deal_input").val();
        $('#title_deal_radio').replaceWith('<p id="title_deal_radio" class="label-new level clean">' + value + '</p>');
        $('#title_deal_radio2').replaceWith('<p id="title_deal_radio2" class="left label-new">' + value + '</p>');
        $('#title_deal_radio3').replaceWith('<p id="title_deal_radio3" class="left label-new">' + value + '</p>');

        $('#title_deal_radio3_input').click();
    }).keydown(function () {
        $('#title_deal_radio3_input').click();        
    });


    $('.deal-mode-list').live('click', function() {
        var $this = $(this),
                filter = $('.deal-data').attr('data-filter'),
                cityId = $('.deal-data').attr('data-cityId'),
                neightbourhoodId = $('.deal-data').attr('data-neightbourhoodId'),
                id = $('.deal-data').attr('data-id');


        $.post([server + "deals/deals_list", cityId, neightbourhoodId, filter, id].join('/'), {}, function(data) {
            $('.mode-list a').addClass('active');
            $('.mode-map a').removeClass('active');
            $('.deal-content').replaceWith(data);


        });

        return false;

    });


    $('.searchtag').live('click', function() {
        var $this = $(this),
                idTag = $this.attr('data-id'),
                filter = 'actives';


        $.post([server + "deals/search_list", idTag].join('/'), {}, function(data) {

            $('.more-results').remove();
            $('.filtering-bar li a').removeClass('active');
            $('.deal-content').replaceWith(data);
            $('.relative a').removeClass('active');
            $('.arrow').remove();

        });

        return false;


    });


    $('.searchcategory').live('click', function() {
        var $this = $(this),
                titleCat = $this.attr('data-title'),
                idCat = $this.attr('data-id');

        $("#categoryTitle").attr('value', titleCat);
        $("#categoryId").attr('value', idCat);

        return false;


    });


    $('.load_more_results').live('click', function() {
        var $this = $(this),
                filter = $this.attr('data-filter'),
                offset = $this.attr('data-offset'),
                cityId = $('.deal-data').attr('data-cityId'),
                neightbourhoodId = $('.deal-data').attr('data-neightbourhoodId'),
                id = $this.attr('data-id');

        $.post([server + "deals/deals_list", cityId, neightbourhoodId,filter,id, offset].join('/'), {}, function(data) {
            $('.more-results').replaceWith(data);
        });
        return false;

    });


    $('.load_more_results_premiumdeals').live('click', function() {
        var $this = $(this),
                offset = $this.attr('data-offset'),
                cont = $this.attr('data-cont'),
                id = $this.attr('data-id');

        $.post([server + "backend/deals_premium_list", id, offset, cont].join('/'), {}, function(data) {
            $('.results-' + cont).replaceWith(data);
        });
        return false;

    });


    $('.load_more_results_backend').live('click', function() {
        var $this = $(this),
                filter = $this.attr('data-filter'),
                offset = $this.attr('data-offset'),
                id = $this.attr('data-id');

        $.post([server + "backend/deals_list",filter,id, offset].join('/'), {}, function(data) {
            $('.more-results').replaceWith(data);
        });
        return false;

    });


    $('.deallist_backend li a').live('click', function() {
        var $this = $(this),
                filter = $this.attr('data-filter');

        $.post([server + "backend/dealsListByStatus", filter].join('/'), {}, function(data) {
            $('.deal_list_backend').html(data);
            $('.deallist_backend li a').removeClass('active');
            $this.addClass('active');
        });

        return false;
    });

    $('.filtering-bar li a').live('click', function() {
        var $this = $(this),
                filter = $this.attr('data-filter'),
                cityId = $('.deal-data').attr('data-cityId'),
                neightbourhoodId = $('.deal-data').attr('data-neightbourhoodId'),
                id = $('.deal-content').attr('data-id');

        $.post([server + "deals/deals_list",cityId, neightbourhoodId, filter,id].join('/'), {}, function(data) {
            $('.deal-content').replaceWith(data);
            $('.filtering-bar li a').removeClass('active');
            $this.addClass('active');
        });

        return false;
    });



    $('#softDeleteClick').live('click', function() {
        var $this = $(this),
            id = $this.attr('data-id');
        $.post([server + "backend/deletecompleteddeal",id].join('/'), {},
                 function(data) {
                     $('#completedDealsA').click();
                });
       return false;
    }); 
    
    $('.playstop').live('click', function() {
        var $this = $(this),
                status = $this.attr('data-status'),
                cont = $this.attr('data-cont'),
                id = $this.attr('data-id');
  
        $.post([server + "backend/status", status,id].join('/'), {},

                function(data) {
                    $('#currentDealsA').click();
                });

        if (status == 1) {
            $this.removeClass('play');
            $this.addClass('pause');
            $this.removeAttr('data-status');
            $this.attr('data-status', "0");
        }
        else {
            $this.removeClass('pause');
            $this.addClass('play');
            $this.removeAttr('data-status');
            $this.attr('data-status', "1");
        }


    });


    $('.notify').live('click', function() {


        $.post([server + "user/notify_me"].join('/'), {},

                function(data) {

                    $('.notify').fadeOut();
                });
        return false;

    });

    $('.delete-image').live('click', function() {

        var $this = $(this),
                id = $this.attr('data-id'),
                cont = $this.attr('data-cont');

        $.post([server + "backend/delete_image",id].join('/'), {},

                function(data) {

                    $('.' + cont).fadeOut();
                });
        return false;

    });


    $('.delete-image-deal').live('click', function() {

        var $this = $(this),
                id = $this.attr('data-id'),
                cont = $this.attr('data-cont');

        $.post([server + "backend/delete_image_deal",id].join('/'), {},

                function(data) {

                    $('.' + cont).fadeOut();
                });
        return false;

    });


    $('.delete-tag').live('click', function() {

        var $this = $(this),
                id = $this.attr('data-id'),
                cont = $this.attr('data-cont');

        $.post([server + "backend/delete_tag",id].join('/'), {},

                function(data) {

                    $('.tag-' + cont).fadeOut();
                });

        return false;

    });


    $('.premium-deal').live('click', function() {

        var $this = $(this),
                id = $this.attr('data-id'),
                status = $this.attr('data-status');

        $.post([server + "backend/premium_deal",id,status].join('/'), {},

                function(data) {


                });


        if (status == 1) {
            $this.addClass('active');
            $this.removeAttr('data-status');
            $this.attr('data-status', "0");
        }
        if (status == 0) {
            $this.removeClass('active');
            $this.attr('data-status', "1");
        }

        return false;


    });

    $('#makepremium').live('click', function() {

        var $this = $(this),
                id = $this.attr('data-id'),
                status = $this.attr('data-status');

        $.post([server + "backend/makepremium",id,status].join('/'), {},

                function(data) {


                });


        if (status == 1) {
            $this.removeAttr('data-status');
            $this.attr('data-status', "0");
            $this.attr('value', "Change to free");
            $('.makepremium-'+id).show();


        }
        if (status == 0) {
            $this.attr('data-status', "1");
            $this.attr('value', "Change to premium");
            $('.makepremium-'+id).hide();


        }

        return false;


    });


    $('.playstop_premium').live('click', function() {

        var $this = $(this),
                id = $this.attr('data-id'),
                status = $this.attr('data-status');

        $.post([server + "backend/playstop_deal",id,status].join('/'), {},

                function(data) {


                });


        if (status == 1) {
            $this.addClass('active');
            $this.removeAttr('data-status');
            $this.attr('data-status', "0");
        }
        if (status == 0) {
            $this.removeClass('active');
            $this.attr('data-status', "1");
        }

        return false;


    });


    $('.paginate-dealOrder').live('click', function() {

        var $this = $(this);


        $this.addClass('active');


    });


    // Button follow in business profile
    $('.followme').live('click', function() {

        var $this = $(this),
                number = $('.number-follow').attr('data-number'),
                id = $this.attr('data-id');

        number = parseInt(number) + parseInt(1);

        $.post([server + "business/follow_me",id].join('/'), {},

                function(data) {

                    $this.fadeOut();
                    $('.followers-list').append(data);
                    $('.number-replace').replaceWith('<span>' + number + '</span>');
                });

        return false;


    });

    // Button follow in business profile
    $('.unfollowme').live('click', function() {

        var $this = $(this),
                idUser = $this.attr('data-idUser'),
                number = $('.number-follow').attr('data-number'),
                idFollow = $this.attr('data-idFollow');

        $number = number - 1;


        $.post([server + "business/unfollow_me",idFollow].join('/'), {},

                function(data) {

                    $this.fadeOut();
                    $('.follow-' + idUser).hide();
                    $('.number-replace').replaceWith('<span>' + $number + '</span>');
                });
        return false;

    });

    // Button follow in business profile
    $('.headimage').live('click', function() {

        var $this = $(this),
                id = $this.attr('data-id');

        $.post([server + "backend/headimage",id].join('/'), {},
            function(data) {
                if ($this.hasClass('noheadimage')) {
                    $this.removeClass('noheadimage')
                        .addClass('active');
                } else if ($this.hasClass('active')) {
                     $('.headimage').removeClass('noheadimage')
                         .addClass('active');
                     $this.addClass('noheadimage')
                         .removeClass('active');
                }
            });

        return false;


    });

     //Business profile sumarry max character helper
     var maxSummary = 140;
     var maxText = '140 character maximum';
     var $summary = $('#summary');
     var $summaryCounter = $('#summary_counter');
     var updateSummaryCounter = function(event) {
         if ( 0 == $summaryCount.length ) return;
         var summaryCount = $summary.val().length;
         $summaryCounter.html(maxText + ' (' + summaryCount + '/' + maxSummary + ')');
         if (maxSummary <= summaryCount && 
                 event.which != 8 && 
                 event.which != 37 && 
                 event.which != 38 &&
                 event.which != 39 && 
                 event.which != 40 &&
                 event.which != 46){
             event.preventDefault();
         }
     };
     if ( 0 != $summary.length ) {
       $summary.val($summary.val().substr(0, 140)); //Handle summaries in the database over 140 characters.
       $summaryCounter.html(maxText + ' (' + $summary.val().length + '/' + maxSummary + ')');
       $summary.keypress(updateSummaryCounter).keydown(updateSummaryCounter).keyup(updateSummaryCounter);
     }
    // Jquery gallery light box
    var $galleryZoom = $('.gallery-zoom');
    if ($galleryZoom != null && $galleryZoom.length > 0) {
        $galleryZoom.lightBox();
    }

    // Button unfollow in backend
    $('.btn-unfollow').live('click', function() {

        var $this = $(this),
                cont = $this.attr('data-cont'),
                id = $this.attr('data-id');

        $.post([server + "business/unfollow_me",id].join('/'), {},

                function(data) {


                });

        $('.follow-' + cont).fadeOut();

    });


    // For adds tags to the deals in backend
    $('.add-tags').live('click', function() {

        var $this = $(this),
                idDeal = $('.edit-deal').attr('data-id'),
                idTag = $this.attr('data-idtag');

        $.post([server + "backend/addtag",idTag,idDeal].join('/'), {},

                function(data) {
                    $('.tag-list').append(data);

                });

        $('.suggestionsBox').hide();
        $('#inputString').val('');

    });

    // Slider Deals

    $('.slider-rounded').roundabout({
        duration: 550,
        btnNext: '.knotis-slider-left',
        btnPrev: '.knotis-slider-right',
        minOpacity: 0.8,
        minScale: 0.95
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


    // For the login form
    $('#login').live('submit', function() {
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            dataType: "json",
            data: $(this).serialize(),
            success: function(data) {

                if (data.success == 'yes') {
                    if (data.redirect == 1) {
                        window.location = '/';
                    }

                    if (data.redirect == 5) {
                        window.location = server + "home";
                    }

                    if (data.redirect == 2) {
                        window.location = server + "backend/dashboard";

                    }

                    if (data.redirect == 4) {
                        window.location = server + "backend/premiumDeals";

                    }
                }

                if (data.success == 'no') {
                    $('#message-log').replaceWith('<p class="message-confirm message-error radius-general txt-size">' + data.message + '</p>');
                }

            }
        })

        return false;
    });


    // For validate forms

    $("#update_deal").validity(function() {

        $("#deal_address").require();

        $("#startdate").require();

        $("#enddate").require();
    });


    $("#name_business").require();// Required:


    $("#forgotpassword").validity(function() {


        $("#mail").require();


    });

    $("#resetpassword").validity(function() {


        $("#password_new").require();


    });


    $("#searchbusiness").validity(function() {


        $("#search_input").require();


    });


    $("#addlinks").validity(function() {


        $("#titleLink").require();

        $("#urlLink").require();

    });


    // For the create a user form
    $('#newuser').live('submit', function() {

     $('#createdP').show();
     $('#createP').hide();

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            dataType: "json",
            data: $(this).serialize(),
            success: function(data) {

                if (data.success == 'yes') {
                    if (data.user == 'premium'){
                        $('.replace').replaceWith('');
                        $('.resultsContainer').replaceWith(data.message);
                    }
                    if (data.user == 'foreverfree'){
                        $('.replace').replaceWith('');
                        $('.resultsContainer').replaceWith('<p class="message-confirm message-info radius-general txt-size">' + data.message + '</p>');
                    }
                    if (data.user == 'normal'){
                       $('.replace').replaceWith('');
                       $('.resultsContainer').replaceWith('<p class="message-confirm message-info radius-general txt-size">' + data.message + '</p>');
                    }
                }
                if (data.success == 'no') {
                         $('#createdP').hide();
                         $('#createP').show();
                    $('#message-log').replaceWith('<p class="message-confirm message-error radius-general txt-size">' + data.message + '</p>');
                }


            }
        })

        return false;
    })
            ;


    // For the create a user form
    $('#deletedeal').live('submit', function() {


        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            dataType: "json",
            data: $(this).serialize(),
            success: function(data) {

                if (data.success == 'yes') {
                    $('.deal-' + data.id).fadeOut();

                }
                if (data.success == 'no') {

                }


            }
        })

        return false;
    })
            ;


        $('#changeqrcode').live('submit', function() {


        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            dataType: "json",
            data: $(this).serialize(),
            success: function(data) {

                if (data.success == 'yes') {
                    $('#ok-' + data.id).hide();
                    $('#ko-' + data.id).hide();
                    $('#ok-' + data.id).show();
                }
                if (data.success == 'no') {
                    $('#ok-' + data.id).hide();
                    $('#ko-' + data.id).hide();
                    $('#ko-' + data.id).show();
                }


            }
        })

        return false;
    })
            ;

    $('#changeuser').live('submit', function() {


    $.ajax({
        type: 'POST',
        url: $(this).attr('action'),
        dataType: "json",
        data: $(this).serialize(),
        success: function(data) {

            if (data.success == 'yes') {
                $('#ok-' + data.id).hide();
                $('#ko-' + data.id).hide();
                $('#ok-' + data.id).show();
            }
            if (data.success == 'no') {
                $('#ok-' + data.id).hide();
                $('#ko-' + data.id).hide();
                $('#ko-' + data.id).show();
            }


        }
    })

    return false;
})
        ;




    $("#pay").live('change', function() {
        var $this = $(this),
                value = $this.attr('data-value'),
                id = $this.attr('data-id');

        $.post([server + "backend/paydeal",id,value].join('/'), {},

                function(data) {

                    if (value == 1) {
                        $this.attr('data-value', "0");
                    }
                    if (value == 0) {
                        $this.attr('data-value', "1");
                    }

                });

    });

        $(".graphic-buttom").live('click', function() {
        var $this = $(this),
                type = $this.attr('data-type'),
                id = $this.attr('data-id');

        $.post([server + "backend/graphic",id,type].join('/'), {},

                function(data) {

                    $('#graphic-' + id).replaceWith(data);


                });

            $(".graphic-buttoms-" + id +" li a").removeClass('active');

            $(this).addClass('active');

             return false;

    });


    $(".qrcode-buttom").live('click', function() {
    var $this = $(this),
            type = $this.attr('data-type'),
            id = $this.attr('data-id');

    $.post([server + "backend/graphicqrcode",id,type].join('/'), {},

            function(data) {

                $('#graphic-' + id).replaceWith(data);


            });

        $(".qrcode-buttoms-" + id +" li a").removeClass('active');

        $(this).addClass('active');

         return false;

});






// For external iframe in business


    //START Facebook js integration

    window.fbAsyncInit = function() {
        var handleSession = function(response, canLogout) {
            if (response.status === "connected") {
                // For now check to see if link account button exists, if does assume using that otherwise its login
                var action = $('#fb-root').attr("data-sign-up-action");

                FB.api('/me', function(user) {
                    $.post(action, {'data' : { 'response': response, 'user' : user}},
                            function(data) {
                                //todo redirect after login if necessary
                                if (data.success == 'yes') {
                                    if (data.user == 'premium')
                                        $('.replace').replaceWith(data.message);

                                    if (data.user == 'foreverfree')
                                        window.location = server + "backend/businessprofile";

                                    if (data.user == 'normal')
                                        window.location.reload(true);
                                }
                                if (data.success == 'no') {
                                    $('#message-log').replaceWith('<p class="message-confirm message-error radius-general txt-size">' + data.message + '</p>');
                                }

                                if (data.success == 'reload') {
                                    window.location.reload(true);
                                }

                            }, 'json');

                });

            } else if (canLogout) {
               var $r = Math.floor(Math.random()*1000000000);
               var location = server + "user/log_out/" + $r;
               window.location = location;
            }
        };

        FB.init({
            appId: facebookAppId,
            status: true,
            cookie: true,
            xfbml: true,
            oauth: true,
            channelUrl: window.location.protocol + '//' + window.location.host + server + 'channel.php'
        });

        FB.Event.subscribe('auth.authResponseChange', function(response) {
            handleSession(response, true);
        });

        FB.getLoginStatus(function(response) {
            handleSession(response, false);
        });
        
        FB.Canvas.setAutoResize();
    };

    (function(d){
       var js, id = 'facebook-jssdk'; if (d.getElementById(id)) {return;}
       js = d.createElement('script'); js.id = id; js.async = true;
       js.src = "//connect.facebook.net/en_US/all.js";
       d.getElementsByTagName('head')[0].appendChild(js);
    }(document));

    //END Facebook js integration

})
        ;

function showImg() {
    var imgActive = $('#rotator img.active');
    $('#controller a').removeClass('selected');
    $('#rotator img.active').fadeOut("normal", function () {
        if ($(this).next('img').attr('src')) {
            $(this).removeClass('active');
            $(this).next('img').fadeIn('slow').addClass('active');
            $("#rotator img").each(function(i, item) {
                if ($(item).hasClass("active")) {
                    $('#controller a:eq(' + (i) + ')').addClass('selected');
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
var intervalgallery = setInterval("showImg()", 10000);

// End Slider Business

// jquery autocomplete in search deals


function lookup_backend(inputString) {


    if (inputString.length == 0) {
        // Hide the suggestion box.
        $('#suggestions').hide();
    } else {
        $.post(server + "backend/autocomplete", {queryString: "" + inputString + ""}, function(data) {
            if (data.length > 0) {
                $('#suggestions').show();
                $('#autoSuggestionsList').html(data);
            }
        });
    }
} // lookup

function lookup_frontend(inputString) {

    if (inputString.length == 0) {
        // Hide the suggestion box.
        $('#suggestions').hide();
    } else {
        $.post(server + "deals/autocomplete", {queryString: "" + inputString + ""}, function(data) {
            if (data.length > 0) {
                $('#suggestions').show();
                $('#autoSuggestionsList').html(data);
            }
        });
    }
} // lookup

function lookup_home(inputString) {

    if (inputString.length == 0) {
        // Hide the suggestion box.
        $('#suggestions').hide();
    } else {
        $.post(server + "home/autocomplete", {queryString: "" + inputString + ""}, function(data) {
            if (data.length > 0) {
                $('#suggestions').show();
                $('#autoSuggestionsList').html(data);
            }
        });
    }
} //

function fill(thisValue) {
    $('#inputString').val(thisValue);
    setTimeout("$('#suggestions').hide();", 200);
}

function loadNeighbourhood() {

    var idCity = $('#citySelect').val();

    if (idCity) {
        $.post([server + "backend/neighbourhood",idCity].join('/'), {},
            function(data) {
              $.uniform.update($('#neighbourhoodSelect').html(data));
            });
    }
}







