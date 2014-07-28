(function($){
    $('#id-start-time').datetimepicker({
        language: 'en',
        pick12HourFormat: true,
        autoclose: true
    });
    $('#id-end-time').datetimepicker({
        language: 'en',
        pick12HourFormat: true,
        autoclose: true
    });

    $('#id_no_time_limit').click(function(){
        if (this.checked){
            $('#id-end-time input').prop('disabled', true).parent().hide('slow');
        } else {
            $('#id-end-time input').prop('disabled', false).parent().show('slow');
        }
    });



})(jQuery);