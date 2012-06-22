from django.shortcuts import render_to_response
from django.template.context import RequestContext

def oauth_callback(request):
  return render_to_response(
    'piston/oauth/callback.html',
    {},
    context_instance=RequestContext(request))
