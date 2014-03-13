(function($) {
    $('.offer-tile').click(function(event) {
        event.preventDefault();

        offer_id = this.getAttribute('data-offer-id');
        $.ajaxmodal({
            href: '/offer/detail/' + offer_id + '/',
            modal_id: 'id-offer-detail',
            modal_width: '750px'
        });
    });

    var upload_logo = function(event) {
        event.preventDefault();

        var identity_id = $('div#id-identity-id').attr('data-business-id')

        $.ajaxmodal({
            href: '/image/upload/',
            modal_settings: {
                backdrop: 'static'
            },
            on_open: function(data, status, request) {
                $('#file-uploader').sickle({
                    do_upload: true,
                    params: {
                        type: 'image',
                    },
                    aspect: 1,
                    primary: true,
                    done: function(data) {
                        if (data.status == 'success') {
			    $img = $('#profile-badge');
			    $img.attr('src', data.image_url);
			    
                        } else if (data.status == 'failure') {
                            
                        } else {
                            // Invalid Status
                        }
                    },
                    related_object_id: identity_id,
                    context: 'profile_badge',
                    jcrop_box_width: 560
                });
            }
        })

    };

    $('.change-profile-badge-link').click(upload_logo);

    // BANNER EDITING

    $('a.change-profile-cover-link').click(function(event){
      event.preventDefault();
      var identity_id = $('#id-identity-id').attr('data-business-id');

      $.ajaxmodal({
          href: '/image/upload',
          modal_settings: {
            backdrop: 'static'
          },
          on_open: function(data, status, request){

            $('#file-uploader').sickle({
                do_upload: true,
                params: {
                  type: 'image'
                },
                aspect: 5.12,
                related_object_id: identity_id,
                context: 'profile_banner',
                primary: true,
                done: function(data){
                  $('modal-box').modal('hide');
                  $('#id-profile-cover').css('background-image', 'url("' + data.image_url + '")');
                },
                jcrop_box_width: 560
            });   
          }
      });
    });

    // carousel
    $('#about_carousel').carousel({
        interval: 5000
    });
    
    $('a.upload-photo').click(function(event){
      event.preventDefault();
      var identity_id = $(this).attr('data-business-id');
        
      $.ajaxmodal({
          href: '/image/upload',
          modal_settings: {
            backdrop: 'static'
          },
          on_open: function(data, status, request){
        
            $('#file-uploader').sickle({
                do_upload: true,
                params: {
                  type: 'image'
                },
                aspect: 1.25,
                related_object_id: identity_id,
                context: 'business_profile_carousel',
                primary: false,
                done: function(data){
                  
                        // stop the carousel
                        $('#about_carousel').carousel('pause').removeData();

                        // populate carousel-inner
                        var uploaded_url = data.image_url;
                        var $img = $('<div style="display:block; width:500px; height:400px; overflow:hidden; background:url(' + uploaded_url + ') no-repeat;"></div>');
                        var $item = $('<div class="item"></div>');
                        $item.append($img);
                        $('#about_carousel>.carousel-inner').append($item);

                        // populate carousel-indicators
                        $indicator = $('<li data-target="#about_carousel" data-slide-to="' + $('#about_carousel>.carousel-indicators').children().size() + '" style="list-style: none;"></li>');
                        $('#about_carousel>.carousel-indicators').append($indicator);
                        
                        // resume the carousel
                        $('#about_carousel').carousel('next');

                        // finally, hide the modal box
                        $('modal-box').modal('hide');
                }
            });
          }
        });
    });

    $('.twitter.tab').click(function(){
        $('.tab-pane#yelp').hide();
        $('li.tab.yelp').removeClass('active');

        $('.tab-pane#twitter').show();
        $('li.tab.twitter').addClass('active');
    });

    $('.yelp.tab').click(function(){
        $('.tab-pane#twitter').hide();
        $('li.tab.twitter').removeClass('active');

        $('.tab-pane#yelp').show();
        $('li.tab.yelp').addClass('active');
    });

    // gather up all the address display elements on the page, and link them. 
    $('.linked-business-name').link_field('linkbizname');
    $('.linked-phone-number').link_field('linkphonenum');
    $('.linkedaddress').link_field('linkaddress');
    $('.linkedwebsite').link_field('linkweb');
    
})(jQuery);
