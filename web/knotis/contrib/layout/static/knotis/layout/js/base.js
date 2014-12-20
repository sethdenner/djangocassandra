;
// Render Forth

(function ($) {
    "use strict";
    $(document).ready(function() {
        $('#mainNavMobileToggle').on("checked", function(){
            $('body').addClass('navOn');
        });
        $('#mainNavMobileToggle').on("unchecked", function(){
            $('body').removeClass('navOn');
        });
        $('#mainNavMobileToggle').on("change", function(){
            if($(this)[0].checked){
                $('#mainNavMobileToggle').trigger("checked");
            }else{
                $('#mainNavMobileToggle').trigger("unchecked");
            };
        });
        $('#mainNavMobileToggle').trigger("change");
        $('.searchButton').on("click", function(){
            var $inputBox;
            if(($inputBox = $(this).parent().find('input:visible')).length){
                if($inputBox.val().length){
                    $(this).parent().find("form").submit();
                    return;
                }
            }
            $(this).parent('div.searchForm').toggleClass('expanded');
        });
    });

})(jQuery);
