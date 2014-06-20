(function($) {
    $.ajaxmodal({
        href: '/identity/first/',
        modal_settings: {
            backdrop: 'static',
            keyboard: false,
        },
        on_open: function(data, status, request) {
            $('#id-individual-form').ajaxform({
                done: function(data, status, jqxhr) {
                    if (!data.errors) {
                        $('#first-carousel')
                            .carousel({interval: false})
                            .carousel('next');

                        $('#modal-box').modal({
                            backdrop: true,
                            keyboard: true
                        });

                    }
                    $('#id-identity-dropdown').text(data.data.individual_name);
                },
                method: 'put'
            });

            $('#id-business-form').ajaxform({
                done: function(data, status, jqxhr) {
                    if (!data.errors) {
                        $('#first-carousel')
                            .carousel({interval: false})
                            .carousel('next');

                        $('#id-location-form #address-input #id_address').geocomplete({
                            map: '.map_canvas',
                            location: 'Seattle, WA, USA',
                            details: '#id-location-form',
                            detailsAttribute: 'data-geo'
                        });

                        $('form#id-location-form input#related-id-input').val(
                            data.data.establishment_id
                        );

                        $('form#id-location-form').append(
                            '<input id="backend_name" type="hidden" value="' +
                                data.data.business_backend_name +
                                '"/>'
                        );

                    }

                }
            });

            $('#id-location-form').ajaxform({
                done: function(data, status, jqxhr) {
                    if (!data.errors) {
                        $('#modal-box').modal('hide');
                        var related_id = $('form#id-location-form input#related-id-input').val();
                        window.location = '/id/' + related_id + '/';

                    }

                }
            });

            $('#first-carousel button#id-button-business').click(function(event) {
                event.preventDefault();
                $('#first-carousel').carousel('next');

            });

            $('#first-carousel button#id-button-offers').click(function(event) {
                event.preventDefault();
                $('#modal-box').modal('hide');

            });
        }
    });

})(jQuery);
