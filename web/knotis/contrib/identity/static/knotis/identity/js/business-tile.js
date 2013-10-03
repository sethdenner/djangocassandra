$(document.ready(function(){

  var getIdentity(e){
    $(this).parent().sibling('.tile-user').val();
  };

  var getCurrentIdentity(e){
    $(this).parent().sibling('.tile-identity').val();
  };

  $('.identity-follow').click(function(e){
    $.post('/api/follow', {
      current_identity_id: getCurrentIdentity(e),
      related_id: getIdentity(e);
    });
  });
  
});
