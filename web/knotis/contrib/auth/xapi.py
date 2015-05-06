from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import (
    APIException,
    MethodNotAllowed
)

from oauth2_provider.ext.rest_framework import OAuth2Authentication

from knotis.views import (
    ApiViewSet,
    ApiModelViewSet
)

from knotis.contrib.rest_framework.authentication import (
    ClientOnlyAuthentication
)

from .api import AuthenticationApi

from .models import (
    UserInformation
)

from .serializers import (
    UserSerializer,
    UserInformationSerializer,
    ResetPasswordSerializer
)

from django.utils.log import logging
logger = logging.getLogger(__name__)


class ResetPasswordApiViewSet(ApiViewSet):
    api_path = 'auth/resetpassword'
    resource_name = 'resetpassword'

    serializer_class = ResetPasswordSerializer
    authentication_classes = (
        SessionAuthentication,
        OAuth2Authentication,
        ClientOnlyAuthentication,
    )
    permission_classes = (AllowAny,)

    allowed_methods = ['POST', 'options']

    def create(
        self,
        request
    ):
        resetpassword_serializer = ResetPasswordSerializer(
            data=dict(request.DATA.iteritems())
        )

        if resetpassword_serializer.errors:
            raise APIException(detail=resetpassword_serializer.errors)

        try:
            AuthenticationApi.reset_password(
                request
            )

        except Exception, e:
            logger.exception(e.message)

        return Response(data={'status': 'OK'})


class NewUserApiViewSet(ApiViewSet):
    api_path = 'auth/new'
    resource_name = 'new'

    serializer_class = UserSerializer
    authentication_classes = (
        SessionAuthentication,
        OAuth2Authentication,
        ClientOnlyAuthentication,
    )
    permission_classes = (AllowAny,)

    allowed_methods = ['POST', 'options']

    def create(
        self,
        request
    ):
        user_serializer = UserSerializer(
            data=dict(request.DATA.iteritems())
        )

        if user_serializer.errors:
            raise APIException(detail=user_serializer.errors)

        user, identity, errors = AuthenticationApi.create_user(
            **user_serializer.data
        )

        if errors:
            raise self.UserCreationError(detail=errors)

        user_info = UserInformation.objects.get(user=user)
        info_serializer = UserInformationSerializer(user_info)
        return Response(info_serializer.data)

    class UserCreationError(APIException):
        status_code = 400


class UserApiModelViewSet(ApiModelViewSet):
    api_path = 'auth/user'
    resource_name = 'user'

    model = UserInformation
    queryset = UserInformation.objects.none()
    serializer_class = UserInformationSerializer
    permission_classes = (AllowAny,)

    allowed_methods = ['GET']

    def retrieve(
        self,
        request,
        pk=None
    ):
        raise MethodNotAllowed(request.method)

    def list(
        self,
        request
    ):
        user_info = UserInformation.objects.get(user=request.user)
        serializer = UserInformationSerializer(user_info)
        return Response(serializer.data)
