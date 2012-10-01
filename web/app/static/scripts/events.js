//ONLY FOR DEVELOPER TIME

if (location.hostname == 'localhost') {
    var server = "http://localhost:8000";
}

else {
    var server = "/";
}

var login = 0;

//

$(function() {

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
    $(document).ajaxSend(         
        function(event, xhr, settings){
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    )

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
            $("#fb-root").attr('data-sign-up-action', '/facebook/login/user/');

        if (type == 'foreverfree')
            $("#fb-root").attr('data-sign-up-action', '/facebook/login/foreverfree/');

        if (type == 'premium')
            $("#fb-root").attr('data-sign-up-action', '/facebook/login/premium/');


        $('.signup_popup').remove();
        $('.log_in_popup').remove();

        $.get("/signup/" + type, {},
                function(data) {
                    $(".header-content").append(data).fadeIn();
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
            window.location = server +"offers/?query=" + string;
        }
    });
    
    $('.link-search').click(function(event) {
       window.location = [
           '/offers/?query=',
           $('#search').val()
       ].join('');
       event.stopPropagation();
       return false;
       
    });
    
    $('#search_form').submit(function(event){
       window.location = [
           '/offers/?query=',
           $('#search').val()
       ].join('');
       event.stopPropagation();
       return false;
        
    });

    // count characters

    $("#title_offer").charCount({
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


    // For categories in the offers page
    $('.categories-filter').live('click', function(evt) {
        var $this = $(this),
            $content = $('.offer-content');
            
        if (!$content.length) {
            return true;
        }
        
        var href = $content.attr('data-href'),
            query = $content.attr('data-query'),
            business = $content.attr('data-business'),
            city = $content.attr('data-city'),
            neighborhood = $content.attr('data-neighborhood'),
            category = $this.attr('data-category'),
            premium = $content.attr('data-premium'),
            page = $content.attr('data-page');

        $content.load_offers();
        $content.load_offers(
            'load', 
            function(
                data,
                jqxhr,
                status 
            ) {
                if (!category) {
                    category = 'All';
                }
                $('.list-backend .relative a').removeClass('active');
                $('.arrow').remove();
                $('.' + category + ' a').addClass('active');
                $('.' + category).append('<div class="arrow arrow-' + category + '"></div>');
                $('.offer-content').html(data);
            }, 
            href,
            business,
            city,
            neighborhood,
            category,
            premium,
            page,
            query
        );
        $(document).load_offers(
            'load_scroll', 
            '.offer-content'
        );

        evt.stopPropagation();
        return false;

    });


// For nodes maps

    $('.offer-mode-map').live('click', function() {
        var $this = $(this),
            $content = $('.offer-content'),
            href = '/offers/offer_map/',
            business = $content.attr('data-business'),
            city = $content.attr('data-city'),
            neighborhood = $content.attr('data-neighborhood'),
            category = $content.attr('data-category'),
            premium = $content.attr('data-premium'),
            page = $content.attr('data-page'),
            query = $content.attr('data-query');

        $content.load_offers();
        $content.load_offers(
            'load',
            function(
                data,
                jqxhr,
                status
            ){
                $(document).load_offers('stop_scroll');
                $('.offer-content').html(data);
                $('.mode-map a').addClass('active');
                $('.mode-list a').removeClass('active');                
            },
            href,
            business,
            city,
            neighborhood,
            category,
            premium,
            page,
            query
        )
        
        return false;

    });

    $('#price_offer_input').keyup(function () {

        var value = $("#price_offer_input").val();
        $('#price_offer_radio').replaceWith('<p id="price_offer_radio" class="left label-new price_offer_radio">$' + value + '</p>');
        $('#price_offer_radio2').replaceWith('<p id="price_offer_radio2" class="left label-new price_offer_radio">$' + value + '</p>');

    });

    $('#old_offer_input').keyup(function () {

        var value = $("#old_offer_input").val();
        $('#old_offer_radio').replaceWith('<p id="old_offer_radio" class="left label-new">$' + value + '</p>');
        $('#old_offer_radio2').replaceWith('<p id="old_offer_radio2" class="left label-new">$' + value + '</p>');

        var value_new = $("#price_offer_input").val();


    });

    var updateDiscount = function(){
        var value = $("#old_offer_input").val();

        var value_new = $("#price_offer_input").val();

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
    
    $('#price_offer_input').change(updateDiscount).keyup(updateDiscount);
    $('#old_offer_input').change(updateDiscount).keyup(updateDiscount);
    updateDiscount();

    $('#title_offer_input').keyup(function () {
        var value = $("#title_offer_input").val();
        $('#title_offer_radio').replaceWith('<p id="title_offer_radio" class="label-new level clean">' + value + '</p>');
        $('#title_offer_radio2').replaceWith('<p id="title_offer_radio2" class="left label-new">' + value + '</p>');
        $('#title_offer_radio3').replaceWith('<p id="title_offer_radio3" class="left label-new">' + value + '</p>');

        $('#title_offer_radio3_input').click();
    }).keydown(function () {
        $('#title_offer_radio3_input').click();        
    });

    $('.offer-mode-list').live('click', function(evt) {
        var $this = $(this),
            $content = $('.offer-content'),
            href = '/offers/get_newest_offers/',
            query = $content.attr('data-query'),
            business = $content.attr('data-business'),
            city = $content.attr('data-city'),
            neighborhood = $content.attr('data-neighborhood'),
            category = $content.attr('data-category'),
            premium = $content.attr('data-premium'),
            page = $content.attr('data-page');
        
        $content.load_offers();
        $content.load_offers(
            'load', 
            function(
                data,
                jqxhr,
                status 
            ) {
                $('.mode-list a').addClass('active');
                $('.mode-map a').removeClass('active');
                $('.offer-content').html(data);
            }, 
            href,
            business,
            city,
            neighborhood,
            category,
            premium,
            page,
            query
        );
        $(document).load_offers(
            'load_scroll', 
            '.offer-content'
        );

        evt.stopPropagation();
        return false;
    });

    var cancelEvent = function(evt){
        evt.stopPropagation()
        return false;
    }
    

    var searchOffers = function(query){
        var $content = $('.offer-content');
        
        if (!$content.length) {
            window.location = '/offers/?query=' + query;
            return false;
        }
        
        var href = $content.attr('data-href'), 
            business = $content.attr('data-business'),
            city = $content.attr('data-city'),
            neighborhood = $content.attr('data-neighborhood'),
            category = $content.attr('data-category'),
            premium = $content.attr('data-premium'),
            page = $content.attr('data-page');
        
        $content.load_offers();
        $content.load_offers(
            'load', 
            function(
                data,
                jqxhr,
                status 
            ) {
                $content.html(data);
            }, 
            href,
            business,
            city,
            neighborhood,
            category,
            premium,
            '1',
            query
        );
        $(document).load_offers(
            'load_scroll', 
            '.offer-content'
        );
    }

    $search = $('#search');

    $search.live('keyup', function(evt){
        searchOffers($search.val());
        return cancelEvent(evt);
    })

    $('.search-offers').live('click', function(evt){
        searchOffers($search.val());        
        return cancelEvent(evt);
    })

    $('.searchtag').live('click', function() {
        var $this = $(this),
                idTag = $this.attr('data-id'),
                filter = 'actives';


        $.post([server + "offers/search_list", idTag].join('/'), {}, function(data) {

            $('.more-results').remove();
            $('.filtering-bar li a').removeClass('active');
            $('.offer-content').replaceWith(data);
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
                cityId = $('.offer-data').attr('data-cityId'),
                neightbourhoodId = $('.offer-data').attr('data-neightbourhoodId'),
                id = $this.attr('data-id');

        $.post([server + "offers/offers_list", cityId, neightbourhoodId,filter,id, offset].join('/'), {}, function(data) {
            $('.more-results').replaceWith(data);
        });
        return false;

    });


    $('.load_more_results_premiumoffers').live('click', function() {
        var $this = $(this),
                offset = $this.attr('data-offset'),
                cont = $this.attr('data-cont'),
                id = $this.attr('data-id');

        $.post([server + "backend/offers_premium_list", id, offset, cont].join('/'), {}, function(data) {
            $('.results-' + cont).replaceWith(data);
        });
        return false;

    });


    $('.load_more_results_backend').live('click', function() {
        var $this = $(this),
                filter = $this.attr('data-filter'),
                offset = $this.attr('data-offset'),
                id = $this.attr('data-id');

        $.post([server + "backend/offers_list",filter,id, offset].join('/'), {}, function(data) {
            $('.more-results').replaceWith(data);
        });
        return false;

    });


    $('.offerlist_backend li a').live('click', function() {
        var $this = $(this),
                filter = $this.attr('data-filter');

        $.get(['/offers/get_offers_by_status', filter, ''].join('/'), {}, function(data) {
            $('.offer_list_backend').html(data);
            $('.offerlist_backend li a').removeClass('active');
            $this.addClass('active');
        });

        return false;
    });

    $('.offers-filter-menu li a').live('click', function(evt) {
        var $this = $(this),
            filter = $this.attr('data-filter'),
            $content = $('.offer-content'),
            query = $content.attr('data-query'),
            business = $content.attr('data-business'),
            city = $content.attr('data-city'),
            neighborhood = $content.attr('data-neighborhood'),
            category = $content.attr('data-category'),
            premium = $content.attr('data-premium');

        var href; 
        if (filter == 'popular'){
            href = '/offers/get_popular_offers/';
        } else if (filter == 'expiring'){
            href = '/offers/get_expiring_offers/';
        } else {
            href = '/offers/get_newest_offers/';
        }
                
        $content.load_offers();
        $content.load_offers(
            'load', 
            function(
                data,
                jqxhr,
                status 
            ) {
                $('.offer-content').html(data);
                $('.filtering-bar li a').removeClass('active');
                $('.mode-list a').addClass('active');
                $('.mode-map a').removeClass('active');
                $this.addClass('active');
                
            }, 
            href,
            business,
            city,
            neighborhood,
            category,
            premium,
            1,
            query
        );
        $(document).load_offers(
            'load_scroll', 
            '.offer-content'
        );

        evt.stopPropagation();
        return false;

    });


    $('#softDeleteClick').live('click', function() {
        var $this = $(this),
            id = $this.attr('data-id');
        $.post([server + "backend/deletecompletedoffer",id].join('/'), {},
                 function(data) {
                     $('#completedOffersA').click();
                });
       return false;
    }); 
    
    $('.playstop').live('click', function() {
        var $this = $(this);
        var active = $this.attr('data-active');
        var cont = $this.attr('data-cont');
        var id = $this.attr('data-id');
  
        active = active.toLowerCase() == 'true' ? false : true;
        $.post(
            '/offers/update/', {
                'offer_id': id,
                'active': active
            }, function(data) {
                $('#currentOffersA').click();
            }
        );

        if (status == 'true') {
            $this.removeClass('play');
            $this.addClass('pause');
            $this.removeAttr('data-status');
            $this.attr('data-status', "0");
        } else {
            $this.removeClass('pause');
            $this.addClass('play');
            $this.removeAttr('data-status');
            $this.attr('data-status', "1");
        }
    });

    $('.notify').live('click', function(evt) {
        $.post('/profile/update/', {
                'notify_offers': true
            }, function(data) {
                $('.notify').fadeOut();
            }
        );
        evt.stopPropagation();
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


    $('.delete-image-offer').live('click', function() {

        var $this = $(this),
                id = $this.attr('data-id'),
                cont = $this.attr('data-cont');

        $.post([server + "backend/delete_image_offer",id].join('/'), {},

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


    $('.premium-offer').live('click', function() {

        var $this = $(this),
                id = $this.attr('data-id'),
                status = $this.attr('data-status');

        $.post([server + "backend/premium_offer",id,status].join('/'), {},

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

        $.post([server + "backend/playstop_offer",id,status].join('/'), {},

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


    $('.paginate-offerOrder').live('click', function() {

        var $this = $(this);


        $this.addClass('active');


    });


    // Button follow in business profile
    $('.followme').live('click', function() {
        var $this = $(this),
                number = $('.number-follow').attr('data-number'),
                id = $this.attr('data-id');

        number = parseInt(number) + parseInt(1);

        $.post(
            '/business/follow/', {
                'business_id': id
            }, function(data) {
                    $this.fadeOut();
                    $('.followers-list').append(data);
                    $('.number-replace').replaceWith('<span>' + number + '</span>');

            }
        );

        return false;
    });

    // Button follow in business profile
    $('.unfollowme').live('click', function() {

        var $this = $(this);
        var id_user = $this.attr('data-iduser');
        var number = $('.number-follow').attr('data-number');
        var id = $this.attr('data-id');

        number = number - 1;

        $.post('/business/unfollow/', {
                business_id: id, 
            }, function(data){
                $this.fadeOut();
                $('.follow-' + id_user).hide();
                $('.number-replace').replaceWith('<span>' + number + '</span>');
            }
        );
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
         if ( 0 == $summaryCounter.length ) return;
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
        var $this = $(this);
        var cont = $this.attr('data-cont');
        var id = $this.attr('data-id');        

        $.post('/business/unfollow/', {
                business_id: id, 
            }, function(data){
                $('.follow-' + cont).fadeOut();
            }
        );
        return false;
    });


    // For adds tags to the offers in backend
    $('.add-tags').live('click', function() {

        var $this = $(this),
                idOffer = $('.edit-offer').attr('data-id'),
                idTag = $this.attr('data-idtag');

        $.post([server + "backend/addtag",idTag,idOffer].join('/'), {},

                function(data) {
                    $('.tag-list').append(data);

                });

        $('.suggestionsBox').hide();
        $('#inputString').val('');

    });

    // Slider Offers

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
                        window.location = server + "backend/premiumOffers";

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

    $("#update_offer").validity(function() {

        $("#offer_address").require();

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
            dataType: 'json',
            data: $(this).serialize(),
            success: function(data) {
                if (data.success == 'no') {
                    $('#createdP').hide();
                    $('#createP').show();
                    $('#message-log').replaceWith(data.html);

                } else if (data.success == 'yes') {
                    $('.replace').replaceWith(data.html);

                }

            }
        })

        return false;
    });

    // For the create a user form
    $('#deleteoffer').live('submit', function() {


        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            dataType: "json",
            data: $(this).serialize(),
            success: function(data) {

                if (data.success == 'yes') {
                    $('.offer-' + data.id).fadeOut();

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
});

    $("#pay").live('change', function() {
        var $this = $(this),
                value = $this.attr('data-value'),
                id = $this.attr('data-id');

        $.post([server + "backend/payoffer",id,value].join('/'), {},

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

        $.ajax({
            dataType: 'html',
            url: [
                '/charts/revenue',
                type,
                ''    
            ].join('/'), 
            success: function(data) {
                $('#graphic-offers').html(data);
            }
        });
        
        $(".graphic-buttom").removeClass('active');
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
                var lock = false;
                FB.api('/me', function(user) {
                    if (lock) { return; }
                    lock = true;
                    
                    $.post(
                        action, {
                            'data' : { 
                                'response': response, 
                                'user' : user
                             }
                         }, 
                         function(data) {
                            if (data.success == 'yes') {
                                if (data.user) {
                                    if (data.user == 'premium') {
                                        $('.replace').replaceWith(data.message);
                                    
                                    }
    
                                    if (data.user == 'foreverfree') {
                                        window.location = '/business/profile/';
                                        
                                    }
    
                                    if (data.user == 'user') {
                                        window.location = '/offers/';
                                        
                                    }
                                    
                                } else {
                                    window.location = '/offers/';
                                    
                                }
            
                            }
                            if (data.success == 'no') {
                                $('#message-log').replaceWith('<p class="message-confirm message-error radius-general txt-size">' + data.message + '</p>');
            
                            }

                            if (data.success == 'reload') {
                                window.location.reload(true);
            
                            }
                            lock = false;
                        }, 
                        'json'
                    );
                });

            } else if (canLogout) {
               var location = "/auth/logout/";
               window.location = location;

            }

        };

        FB.init({
            appId: facebookAppId,
            status: true,
            cookie: true,
            xfbml: true,
            oauth: true,
            channelUrl: window.location.protocol + '//' + window.location.host + '/facebook/channel/'
        });
        
        FB.Event.subscribe('auth.authResponseChange', function(response) {
            handleSession(response, true);
        });

        FB.Canvas.setAutoGrow();
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

// jquery autocomplete in search offers


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
        $.post(server + "offers/autocomplete", {queryString: "" + inputString + ""}, function(data) {
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
        $.get(["/neighborhood",idCity, ''].join('/'), {},
            function(data) {
              $.uniform.update($('#neighbourhoodSelect').html(data));
            });
    }
}







