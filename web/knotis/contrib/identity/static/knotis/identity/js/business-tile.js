(function($){
    
    var getCurrentIdentity = function(btn){
	return $(btn).parent().siblings('.tile-user').val();
    };

    var getRelatedIdentity = function(btn){
	return $(btn).parent().siblings('.tile-identity').val();
    };
    
    var click_follow = function(){

	var btn = $(this);

	$.post('/api/v1/relation/follow/', {
	    current_identity_id: getCurrentIdentity(btn),
	    related_id: getRelatedIdentity(btn),
	    verb: 'follow'
	}, function(response){

	    if(!response.errors['no-field']){
		$(btn).off('click', click_follow);
		
		$(btn).removeClass('tile-identity-follow');
		$(btn).addClass('tile-identity-unfollow');
		
		$(btn).text('Unfollow');
		$(btn).on('click', click_unfollow);
	    }

	    console.log(response);

	});

    };

    var click_unfollow = function(){
	
	var btn = $(this).get();

	$.post('/api/v1/relation/follow/', {
	    current_identity_id: getCurrentIdentity(btn),
	    related_id: getRelatedIdentity(btn),
	    verb: 'unfollow'
	}, function(response){
	    if(!response.errors['no-field']){
		$(btn).off('click', click_unfollow);
		
		$(btn).removeClass('tile-identity-unfollow');
		$(btn).addClass('tile-identity-follow');
		
		$(btn).text('Follow');
		$(btn).on('click', click_follow);
	    }
	});    
    };

    $('.tile-identity-follow').on('click', click_follow);
    $('.tile-identity-unfollow').on('click', click_unfollow);

})(jQuery);
