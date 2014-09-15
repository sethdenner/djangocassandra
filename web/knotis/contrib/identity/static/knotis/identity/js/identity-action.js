;
(function($){
    $.fn.identity_action = function () {
        var $this = $(this);
        var $action_button = $this.find('[data-id=action-button]');
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

        };

        var setupUnfollow = function($element, relation_id) {
            $element.attr('data-method', 'delete');

        };

        var logged_in = 0 != $('div#identity-switcher').length;

        $action_button.actionButton({
            onHover: function($element){
                if (logged_in) {
                    var element = $element.get(0);

                    request_data = {}
                    for (key in data) {
                        request_data[key.replace('-', '_')] = data[key];
                    }

                    var href = $action_button.attr('href');
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
                            $element.text(button_text);
                        },
                        'json'
                        );

                }
            },
                onClickResponse: function(data, status, request, $element){
                    if (logged_in) {
                        if (!$.isEmptyObject(data.errors)) {
                            var button_text = 'Error';

                        } else if ($.isEmptyObject(data.relation) || data.relation.deleted) {
                            setupFollow($element);
                            var button_text = 'Follow';

                        } else {
                            setupUnfollow($element, data.relation.id);
                            var button_text = 'Unfollow';

                        }
                        $element.text(button_text);
                    }
                }
        });
    }
})(jQuery);
