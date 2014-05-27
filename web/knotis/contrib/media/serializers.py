from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    URLField
)

from models import (
    Image,
    ImageInstance
)


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image


class ImageInstanceSerializer(ModelSerializer):
    class Meta:
        model = ImageInstance

    image = ImageSerializer()


class CroppedImageUrlSerializer(ModelSerializer):
    class Meta:
        model = ImageInstance
        fields = ('url',)

    url = URLField(
        read_only=True,
        source='cropped_url'
    )
