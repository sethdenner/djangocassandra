(function($){
    $(function(){
        var $carousel = $('[data-wizard-name=offer_create].carousel'),
        $create_header_title = $('.create-header .create-header-title');

        var init_step_click_handler = function() {
            $('.create-header .create-step.on').off('click.offerwizard').on('click.offerwizard', function(event){
                event.preventDefault();
                event.stopPropagation();

                $this = $(this);
                var current_step = parseInt($carousel.attr('data-current-step')),
                step_order = parseInt($this.attr('data-step-order'));
                
                if (current_step != step_order) {
                    $.wizard.step($carousel, {index: step_order });
                    var step_title = $this.attr('data-header-title');
                    $create_header_title.text(step_title);
                }
            });
        }

        $carousel.wizard('init', {
            step_callback: function(index) {
                $('.create-header .create-step.off[data-step-order=' + index + ']')
                    .removeClass('off')
                    .addClass('on');

                init_step_click_handler();
            }
        });

        var current_step_string = $carousel.attr('data-current-step'),
        header_title = $('.create-step[data-step-order=' + current_step_string + ']')
            .attr('data-header-title');

        $create_header_title.text(header_title);
        
        var current_step = parseInt(current_step_string);
        $('.create-step').each(function(index, element) {
            $element = $(element);
            var step_order = parseInt($element.attr('data-step-order'));
            if (step_order <= current_step) {
                $element.removeClass('off').addClass('on');
            }
        });

        init_step_click_handler();

    });
})(jQuery);
