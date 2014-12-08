(function($){
    "use strict";
    $(function () {
        if (!String.prototype.trim) {
          String.prototype.trim = function () {
              return this.replace(/^\s+|\s+$/g, '');
          };
        }

        if (!String.prototype.startsWith) {
          Object.defineProperty(String.prototype, 'startsWith', {
              enumerable: false,
              configurable: false,
              writable: false,
              value: function (searchString, position) {
                position = position || 0;
                return this.indexOf(searchString, position) === position;
              }
          });
        }



        $('a.edit_about').click(function(event){
          $('#about-us .toggleable').toggle();
            $('.edit_about').hide();
            $('.close_edit_about').show();

          // submit form handler
            $('#submit-business-info').click(function(e){
                e.preventDefault();
                e.stopPropagation();

                // collect form info
                var changed_endpoints = {};
                var changed_name;
                var changed_description;

                var establishment_id = $('#establishment-id').val();

                $('.edit-endpoint').each(function(idx, element){
                    var $element = $(element);
                    var id = $element.attr('id');

                    if(id.startsWith('endpoint')){
                        changed_endpoints[id] = {
                            'endpoint_id': $element.attr('data-endpoint-id'),
                            'endpoint_type': $element.attr('data-endpoint-type'),
                            'endpoint_value': $element.val()
                        };
                    }else if(id == 'business-name'){
                        changed_name = $element.val();
                    }else if(id == 'business-description'){
                        changed_description = $element.val().trim();
                    }
                });

                var info = {};
                info.establishment_id = establishment_id;
                if(changed_name){
                    info.changed_name = changed_name;
                }
                info.changed_endpoints = changed_endpoints;
                info.changed_description = changed_description;

                $.ajax({
                    url: '/id/update_establishment/',
                    data: {data:JSON.stringify(info)},
                    method: 'POST',
                    success: function(response){
                        if(response.status == 'ok'){

                            location.reload(true);
                        }
                    }
                });
            });
        });

        $('.close_edit_about').click(function(){
            $('#about-us .toggleable').hide();
            $('.close_edit_about').hide();
            $('.edit_about').show();
        });

        $('a#business-address').on('click', function(){
            var $this = $(this);
            var current_location = $this.text();

            $.ajaxmodal({
                href: '/location_form/',
                modal_settings: {
                    backdrop: 'static',
                    keyboard: true
                },

                on_open: function(data, status, request){
                    $('form#id-location-form input#related-id-input').val(
                        $('#establishment-id').val()
                    );

                    var geocomplete_input = $("#location-input")

                    geocomplete_input.geocomplete({
                        map: '.map_canvas',
                        details: '#id-location-form',
                        detailsAttribute: "data-geo",
                        location: current_location ? current_location : "Seattle, WA"
                    });

                    var zoom = geocomplete_input.geocomplete("map").getZoom();
                    // Google maps breaks in a bootstrop modal.
                    setTimeout(function () {
                        var map = geocomplete_input.geocomplete("map");
                        var marker = geocomplete_input.geocomplete("marker");
                        google.maps.event.trigger(map, 'resize');
                        map.setCenter(marker.getPosition());
                        map.setZoom(zoom);
                    }, 700);

                    $("#location-search").click(function(){
                        $("#location-input").trigger("geocode");
                    });

                    $('#id-location-form').ajaxform({
                        done: function(data, status, jqxhr){
                            if(!data.errors){

                            $('#modal-box').modal('hide');
                            if(data.location_address) {
                                $('a#business-address').attr({
                                    'data-latitude': data.latitude,
                                    'data-longitude': data.longitude,
                                    'value':data.location_address
                                });

                                $('a#business-address').text(data.location_address);
                            }
                            }
                        }
                    });
                }
            });
        });
    });

})(jQuery);
