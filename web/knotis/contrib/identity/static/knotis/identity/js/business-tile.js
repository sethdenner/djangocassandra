(function($){

    if (undefined === $.identity) {
        $.identity = {};
    }

    $.identity.initialize_business_tiles = function() {
        $('.grid-tile.small-tile.identity-tile').click(function(event) {
            event.preventDefault();
            event.stopPropagation();

            var identity_id = $(this).find('input.tile-identity').val();
            window.location = '/id/' + identity_id;
            return;

        }).each(function(i) {
            var $this = $(this);
            var $action_button = $this.find('.btn.btn-knotis-action');
            var href = $action_button.attr('href');
            var data = {};
            if ($action_button.length) {
                $.each($action_button.get(0).attributes, function(i, attribute) {
                    if (attribute.name.substring(0, 'data-param-'.length) != 'data-param-') {
                        return true;
                    }
                    data[attribute.name.replace('data-param-', '')] = attribute.value;
                });
            }
            var setupFollow = function($element) {
                $element.attr('data-method', 'post');
                $element.attr('href', href);
                for (var key in data) {
                    $element.attr('data-param-' + key, data[key]);
                }
            };

            var setupUnfollow = function($element, relation_id) {
                $element.attr('data-method', 'delete');
                $element.attr('href', [
                    href,
                    relation_id,
                    '/'
                ].join(''));
                var element = $element.get(0);
                var remove_attributes = []
                $.each(element.attributes, function(i, attribute) {
                    if (attribute.name.substring(0, 'data-param-'.length) != 'data-param-') {
                        return true;
                    }
                    remove_attributes.push(attribute.name);
                });
                for (var i = 0; i < remove_attributes.length; ++i){
                    $element.removeAttr(remove_attributes[i]);
                }

            };

            $action_button.actionButton({
                onHover: function($element){
                    var element = $element.get(0);

                    request_data = {}
                    for (key in data) {
                        request_data[key.replace('-', '_')] = data[key];
                    }

                    $.get(
                        href,
                        $.param(request_data),
                        function(data, status, request) {
                            if (!$.isEmptyObject(data.errors)) {
                                var button_text = 'Error';

                            } else if ($.isEmptyObject(data.relations)) {
                                setupFollow($element);
                                var button_text = 'Follow';

                            } else {
                                setupUnfollow($element, Object.keys(data.relations)[0]);
                                var button_text = 'Unfollow';

                            }
                            $element.children('span').text(button_text);
                        },
                        'json'
                    );
                },
                onClickResponse: function(data, status, request, $element){
                    if (!$.isEmptyObject(data.errors)) {
                        var button_text = 'Error';

                    } else if ($.isEmptyObject(data.relation) || data.relation.deleted) {
                        setupFollow($element);
                        var button_text = 'Follow';

                    } else {
                        setupUnfollow($element, data.relation.id);
                        var button_text = 'Unfollow';

                    }
                    $element.children('span').text(button_text);
                }
            });
        });
    };

    $(function() {
        $.identity.initialize_business_tiles();
    });
})(jQuery);
