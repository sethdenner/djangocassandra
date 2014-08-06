(function ($) {
    $(function () {
        $('#id-save-for-later').click(function (e) {
            e.preventDefault();
            e.stopPropagation();

            $('#offer-create.modal').modal('hide');

            return false;

        });

    });

})(jQuery);