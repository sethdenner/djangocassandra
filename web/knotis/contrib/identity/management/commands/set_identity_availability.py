from django.core.management.base import BaseCommand
from knotis.contrib.identity.models import (
    IdentityBusiness,
    IdentityEstablishment
)

from knotis.contrib.media.models import ImageInstance


class Command(BaseCommand):
    def handle(
        self,
        *args,
        **kwargs
    ):
        establishments = IdentityEstablishment.objects.all()
        for establishment in establishments:
            business = (
                IdentityBusiness.objects.get_establishment_parent(
                    establishment
                )
            )

            try:
                profile_badge_image = ImageInstance.objects.get(
                    related_object_id=establishment.id,
                    context='profile_badge',
                    primary=True
                )

            except:
                profile_badge_image = None

            if not profile_badge_image:
                try:
                    profile_badge_image = ImageInstance.objects.get(
                        related_object_id=business.pk,
                        context='profile_badge',
                        primary=True
                    )

                except:
                    pass

            try:
                profile_banner_image = ImageInstance.objects.get(
                    related_object_id=establishment.id,
                    context='profile_banner',
                    primary=True
                )

            except:
                profile_banner_image = None

            if not profile_banner_image:
                try:
                    profile_banner_image = ImageInstance.objects.get(
                        related_object_id=business.pk,
                        context='profile_banner',
                        primary=True
                    )

                except:
                    pass

            available = profile_badge_image and profile_banner_image
            establishment.available = business.available = available
            establishment.save()
            business.save()
