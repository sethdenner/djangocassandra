(function($){
    $('label').click(function() {
      var checkbox = $('#' + $(this).attr('for'));
      if (checkbox.is(':checked')) {
        checkbox.removeAttr('checked');
      } else {
        checkbox.attr('checked', 'checked');
      }
      checkbox.trigger("change");
    });
    $('#mainNavMobileToggle').on("change", function(){
        var sideNavBar = document.getElementById("sideBarNav");
        var width = $(window).innerWidth();
        if( $(this)[0].checked){
            if(width < 800){
                $(sideNavBar).find('.mainNavOverlay').css({display: "block"});
            }else{
                $('body').css({"padding-left": "100px"});                
            }
            $(sideNavBar).find('.navList').each(function(){$(this).css({"left": "0px"})});
            $(sideNavBar).css({"width": "100%"});
            $(sideNavBar).css({"max-width": "100%"});
        }else{
            $(sideNavBar).find('.mainNavOverlay').each(function(){$(this).css({display: "none"})});
            $(sideNavBar).find('.navList').each(function(){$(this).css({"left": "-250px"})});
            $(sideNavBar).css({"max-width": "1px"});
        }
    });
    $("div.searchForm input").val("SEARCH");
    $("div.searchForm input").on("focus", function(){
        if($(this).val().toLowerCase()=="search"){
            $(this).val("");
        }
    });
    $("div.searchForm input").on("blur", function(){
        if($(this).val().toLowerCase()==""){
            $(this).val("SEARCH");
        }
    });
    $('#mainNavMobileToggle').trigger("change");
})(jQuery);
