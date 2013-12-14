(function($){
  
    if (!String.prototype.trim) {
      String.prototype.trim = function () {
          return this.replace(/^\s+|\s+$/g, '');
      };
    }
    
    // endpoint editing
    var comparator = function($element){
      var init = ($element.attr('data-initial-value') || '').trim();
      var current = ($element.val() || '').trim();
      if(init != current){
            if(current == ''){
                return true;
            }

          return current;
      }

      return false;
    };

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

    var endpoint_id_to_type = {
        0: 'email',
        1: 'phone',
        3: 'twitter',
        4: 'facebook',
        5: 'yelp',
        9: 'website',
        10: 'link'
    };

    var endpoint_type_to_id = {
        'email': 0,
        'phone': 1,
        'twitter': 3,
        'facebook': 4,
        'yelp': 5,
        'website': 9,
        'link': 10
    };

    /*
      Takes one updated endpoint of the kind returned in a call to update_profile/ and
      displays the corresponding endpoints on the profile header.
     */
    var header_display_updated_endpoint = function(updated){
        var endpoint_type = updated['endpoint_type'];
        var $cover_endpoint;
        if (endpoint_type == 1){
            $cover_endpoint = $('.cover-endpoint.phone');
            $cover_endpoint.children('span').text(updated['value']);
            $cover_endpoint.attr('href', updated['url']);
        }
        if (endpoint_type == 9){
            $cover_endpoint = $('.cover-endpoint.website');
            $cover_endpoint.children('span').text(updated['value']);
            $cover_endpoint.attr('href', updated['url']);
        }
    };

    /*
      Displays endpoint elements on the edit form.
      Toggle the Edit prompt to Save.
     */

    var form_display_updated_endpoint = function(updated){
        var $form_endpoint = $('[data-endpoint-type="' + updated['endpoint_type'] + '"]');
        
        var new_value = updated['value'];
        var endpoint_id = updated['pk'] || $form_endpoint.attr('data-endpoint-id');

        $form_endpoint.attr({
            'data-initial-value': new_value,
            'data-endpoint-id': endpoint_id
        });
    };

    $('a.edit_about').click(function(event){
      $('#about-us .toggleable').toggle();
        $('.edit_about').hide();
        $('.close_edit_about').show();

      // prepopulate endpoints
      $('.edit-endpoint:not(.description):not(#business-address)').each(function(idx, element){
          $(element).val($(element).attr('data-initial-value') || '');
      });
      
      // submit form handler
      $('#submit-business-info').click(function(e){
          e.preventDefault();
          e.stopPropagation();
          
          // collect form info
          var changed_endpoints = {};
          var changed_name;
          var changed_description;

          var business_id = $('#id-business-id').val();

          $('.edit-endpoint').each(function(idx, element){
            var $element = $(element);
            var id = $element.attr('id');

            var changed = comparator($element);
            if (changed){
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
            }
          });

          var info = {};
          info.business_id = business_id;
          if(changed_name){
            info.changed_name = changed_name;
          }
          info.changed_endpoints = changed_endpoints;
          info.changed_description = changed_description;

          $.ajax({
            url: '/identity/update_profile/',
            data: {data:JSON.stringify(info)},
            method: 'POST',
            success: function(response){
                if(response.status == 'ok'){
                  
                        location.reload(true);
/*
                  // backpopulate changed info
                  for(var endpoint in response.changed_endpoints){
                      $(endpoint.endpoint_id).attr({
                        'data-initial-value': endpoint.endpoint_value,
                        'data-endpoint-id': endpoint.pk
                      });
                  }

                  // update social buttons
                  for(var i=0; i<response.updated_endpoints.length; i++){
                      var endpoint = response.updated_endpoints[i];
                            
                            form_display_updated_endpoint(endpoint);
                            header_display_updated_endpoint(endpoint);
                  }

                        for(var i=0; i<response.deleted_endpoints.length; i++){
                            var endpoint = response.deleted_endpoints[i];
                            
                            $('.cover-endpoint.' + endpoint_id_to_type[endpoint['endpoint_type']]).remove();
                            $('#about-us-form>[data-endpoint-type="' + endpoint['endpoint_type'] + ']').val('');
                        }

                  // Update business name on profile page
                        $('#about-us-form.toggleable').hide();

                        // replace the close without saving button with the edit button
                        $('.close_edit_about').hide();
                        $('.edit_about').show();

*/                        
                }
            }
          });
      });
    });

    $('.close_edit_about').click(function(){
        $('.edit-endpoint').each(function(i, item){
            $(item).val($(item).attr('data-initial-value'));
        });
        $('#about-us .toggleable').hide();
        $('.close_edit_about').hide();
        $('.edit_about').show();
    });

    // address edit
    var $updateable_addresses = $('a#business-address');
    var update_address = function(){
      var $this = $(this);
      $.ajaxmodal({
          href: '/location_form/',
          modal_settings: {
            backdrop: 'static',
            keyboard: true
          },
          on_open: function(data, status, request){
            
            $('#id-location-form').ajaxform({
                done: function(data, status, jqxhr){
                  if(!data.errors){
                      $this.text($('#id_address').val());
                      $('a#business-address').attr({
                        'data-latitude': data.latitude,
                        'data-longitude': data.longitude
                      });
                      $('#modal-box').modal('hide');
                      $('.cover-endpoint.address>.cover-endpoint-text').text(data.location_address);
                      
                      $.fn.link_field.external_update('linkaddress', $('#id_address').val());
                      
                      var latLng = new google.maps.LatLng(parseFloat(data.latitude),
                                                          parseFloat(data.longitude));
                      
                      
                  }
                }
            });
            
            $('#id-location-form #address-input #id_address').geocomplete({
                map: '.map_canvas',
                location: $this.text(),
                details: '#id-location-form',
                detailsAttribute: 'data-geo'
            });

            $('form#id-location-form input#related-id-input').val(
                $('#id-identity-id').attr('data-establishment-id')
            );
          }
      });
    };

    $updateable_addresses.on('click', update_address);
    
    // display the map on the about page. 

    // display the map on the about page. 
    
    var latLng = new google.maps.LatLng(parseFloat($('#establishment-contact-loc-details').attr('data-latitude')),
                              parseFloat($('#establishment-contact-loc-details').attr('data-longitude')));
  
    var setupMap = function(latLng){   
        var map;
        var initialize = function(){
          var mapOptions = {
              center: latLng,
              zoomControl: false,
              scaleControl: false,
              draggable: false,
              navigationContol: false,
              mapTypeId: google.maps.MapTypeId.ROADMAP,
              zoom: 16
          };
          map = new google.maps.Map(document.getElementById('about-map'), mapOptions);

          var markerOptions = {
              position: latLng,
              map: map
          };
          var marker = new google.maps.Marker(markerOptions);
            map.setZoom(16);
        }
        
        google.maps.event.addDomListener(window, 'load', initialize);
        google.maps.event.trigger(map, 'resize');

        return {marker: marker, map: map};
    };
    var map_stuff = setupMap();

})(jQuery);
