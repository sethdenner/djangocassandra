;
(function($) {
    $.fn.identity_action = function() {
        var $this = $(this);
        var $action_button = $this.find('[data-id=action-button]');
        var data = {};

        var setupFollow = function($element) {
            $element.attr('method', 'post');
            var $method_input = $element.find('input[name=method]');
            $method_input.val('post');
        };

        var setupUnfollow = function($element) {
            $element.attr('method', 'delete');
            var $method_input = $element.find('input[name=method]');
            $method_input.val('delete');

        };

        var logged_in = 0 != $('div#identity-switcher').length;

        $action_button.actionButton({
            onClickResponse: function(data, status, request, $element) {
                if (logged_in) {
                    if (!$.isEmptyObject(data.errors)) {
                        var button_text = 'Error';

                    } else if ($.isEmptyObject(data.relation) || data.relation.deleted) {
                        setupFollow($element);
                        var button_text = 'Follow';

                    } else {
                        setupUnfollow($element);
                        var button_text = 'Unfollow';

                    }
                    $button = $element.find('[data-id=form-button]');
                    $button.val(button_text);
                }
            }
        });
    }
})(jQuery);

