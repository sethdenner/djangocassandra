from rest_framework.serializers import Serializer

from knotis.contrib.offer.models import Offer
from knotis.contrib.identity.models import Identity

from knotis.contrib.offer.serializers import OfferSerializer
from knotis.contrib.identity.serializers import IdentitySerializer


class SearchSerializer(Serializer):
    def get_default_fields(self):
        if None is not self.object:
            if hasattr(self.object, 'object'):
                obj = self.object.object
                if isinstance(obj, Identity):
                    model_serializer = IdentitySerializer(instance=self.object)

                elif isinstance(obj, Offer):
                    model_serializer = OfferSerializer(instance=self.object)

                return {'object': model_serializer}

        return {}
