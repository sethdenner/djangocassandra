
(function($) {
    $(function () {

        // carousel
        $('#about_carousel').carousel({
            interval: 5000
        });

        $('a.upload-photo').click(function(event){
            event.stopPropagation();
            event.preventDefault();
            var establishment_id = $('#establishment-id').val();

            $.ajaxmodal({
                href: '/image/upload/',
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
                        related_object_id: establishment_id,
                        context: 'business_profile_carousel',
                        primary: false,
                        image_max_height: 400,
                        image_max_width: 500,
                        done: function(data){

                            // stop the carousel
                            $('#about_carousel').carousel('pause').removeData();

                            // populate carousel-inner
                            var uploaded_url = data.image_url;
                            //$('.about-carousel-image').attr('style')
                            //
                            var numb_images = $('#about_carousel>.carousel-indicators').children().size();

                            var $img = $('<div class="about-carousel-image" style="background:url(' + uploaded_url + ')"></div>');
                            var $item = $('<div class="item"></div>');
                            $item.append($img);
                            $('#about_carousel>.carousel-inner').append($item);

                            // populate carousel-indicators
                            $indicator = $('<li data-target="#about_carousel" data-slide-to="' + $('#about_carousel>.carousel-indicators').children().size() + '" style="list-style: none;"></li>');
                            $('#about_carousel>.carousel-indicators').append($indicator);

                            // resume the carousel
                            if(numb_images == 0) {
                                $item.addClass('active')
                                $indicator.addClass('active');
                            } else {
                                $('#about_carousel').carousel('next');
                            }

                            // finally, hide the modal box
                            $('modal-box').modal('hide');
                        }
                    });
                }
            });
        });

        $('a.delete-x').click(function(event) {
            event.stopPropagation();
            event.preventDefault();

            var $this = $(this);
            $.ajax(
                $this.attr('data-href'), {
                    type: $this.attr('data-method'),
                    data: {
                        pk: $this.attr('data-pk')
                    }
                }
            ).done(function(data, status, jqxhr){
                if (data.errors) {
                    var message = 'An error has occured.';
                    if (data.errors.exception) {
                        message = data.errors.exception;
                    }
                    alert(message);
                } else {
                    $('#about_carousel').carousel('next');
                    $this.parent().remove();

                }
            });

        });
        var $twitter_content = $('[data-id=id-twitter-content]')
        var $yelp_content = $('[data-id=id-yelp-content]')

        $('a[data-id=id-twitter-icon]').click(function(){
            if(!$twitter_content.hasClass('active'))
            {
                event.stopPropagation();
                event.preventDefault();
                $yelp_content.hide();
                $yelp_content.removeClass('active');

                $twitter_content.show();
                $twitter_content.addClass('active');
            }
        });

        $('a[data-id=id-yelp-icon]').click(function(){
            if(!$yelp_content.hasClass('active'))
            {
                event.stopPropagation();
                event.preventDefault();
                $twitter_content.hide();
                $twitter_content.removeClass('active');

                $yelp_content.show();
                $yelp_content.addClass('active');
            }
        });


        $('.profileActionButton').identity_action();

        // display the map on the about page.
        var setupMap = function(){
            var map;
            var marker;
            var initialize = function(){
                var address = $('#establishment-contact-loc-details').attr('data-address');
                var latitude = parseFloat($('#establishment-contact-loc-details').attr('data-latitude'));
                var longitude = parseFloat($('#establishment-contact-loc-details').attr('data-longitude'));
                // Coordinates for Seattle.
                if((!latitude && longitude)) {
                    latitude = 47.6038321;
                    longitude = -122.3300624;
                }
                var latLng = new google.maps.LatLng(latitude,longitude);

                if (!latLng) {
                    return null;

                }

                var mapOptions = {
                    center: latLng,
                    zoomControl: false,
                    scaleControl: false,
                    draggable: false,
                    navigationContol: false,
                    disableDefaultUI: true,
                    mapTypeId: google.maps.MapTypeId.ROADMAP,
                    zoom: 16
                };

                var mapDom = document.getElementById('about-map');
                if (!mapDom) {
                    return null;

                }

                map = new google.maps.Map(document.getElementById('about-map'), mapOptions);
                if (!map) {
                    return null;

                }

                var markerOptions = {
                    position: latLng,
                    map: map,
                };

                marker = new google.maps.Marker(markerOptions);
                google.maps.event.trigger(map, 'resize');

            }

            initialize();

            return {marker: marker, map: map};
        };
        var map_stuff = setupMap();
    });

})(jQuery);
