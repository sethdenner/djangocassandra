from django.utils.log import logging
logger = logging.getLogger(__name__)

from .models import Identity


class GetCurrentIdentityMixin(object):
    @staticmethod
    def _get_current_identity_pk(request):
        current_identity_pk = None

        # First check for current_identity in query params or post data.
        if hasattr(request, 'DATA'):
            current_identity_pk = request.DATA.get('current_identity')

        elif hasattr(request, 'POST'):
            current_identity_pk = request.POST.get('current_identity')

        if current_identity_pk:
            return current_identity_pk

        if hasattr(request, 'QUERY_PARAMS'):
            current_identity_pk = request.QUERY_PARAMS.get('current_identity')

        elif hasattr(request, 'GET'):
            current_identity_pk = request.GET.get('current_identity')

        if current_identity_pk:
            return current_identity_pk

        # Then check in session.
        current_identity_pk = request.session.get('current_identity')
        if current_identity_pk:
            return current_identity_pk

        # Then check for header.
        current_identity_pk = request.META.get('HTTP_CURRENT_IDENTITY')

        return current_identity_pk

    def get_current_identity(
        self,
        request
    ):
        self.current_identity = None

        current_identity_pk = self._get_current_identity_pk(request)

        if not current_identity_pk:
            return self.current_identity

        try:
            self.current_identity = Identity.objects.get(
                pk=current_identity_pk
            )

        except Exception, e:
            logger.exception(e.message)

        return self.current_identity
