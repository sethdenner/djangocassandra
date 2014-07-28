;

(function($){

    $.ajaxmodal = function(options){
        var defaults = {
            href: '#',
            data: 'format=json',
            modal_id: 'modal-box',
            modal_cssclass: 'modal fade',
            modal_width: '',
            modal_template: '<div id="{{ modal_id }}" class="{{ modal_cssclass }}" tabindex="-1" data-width="{{ modal_width }}"></div>',
            modal_settings: {
                backdrop: true,
                keyboard: true
            },
            loading: false,
            on_open: function(data, status, request) {},
            on_close: function(modal) {}
        };
        var settings = $.extend(
            {},
            defaults,
            options
        );

        var build_modal = function() {
            var $modal = $(settings.modal_template.replace('{{ modal_id }}', settings.modal_id)
                           .replace('{{ modal_cssclass }}', settings.modal_cssclass)
                           .replace('{{ modal_width }}', settings.modal_width));
            $('body').append($modal);
            $modal.modal(settings.modal_settings);
            return $modal;
        };

        if (settings.loading) {
            $('body').modalmanager('loading');
        }

        var $modal = $('#' + settings.modal_id);
        if (0 == $modal.length) {
            $modal = build_modal();
        }
        $.get(
            settings.href,
            settings.data,
            function(data, status, request) {
                if (data) {
		            var $html = null;
		            if (typeof data.html !== typeof undefined) {
			            $html = $(data.html);

		            } else {
			            $html = $(data);

		            }
			        
                    if ($html.hasClass('modal')) {
                        $modal = $html;

                    } else {
                        $modal.html($html);

                    }

                    $modal.modal(settings.modal_settings);
                    $modal.on('hidden.bs.modal', settings.on_close);
                    settings.on_open(data, status, request);
                } else {
                    $modal.modal('hide');
                    $modal.remove();

                }
            }
        );
    }

})(jQuery);
