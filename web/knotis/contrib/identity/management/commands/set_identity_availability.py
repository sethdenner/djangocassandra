import time

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
        page = 0
        count = 20
        establishments = IdentityEstablishment.objects.filter(
            available=False
        )[page:page + count]
        while len(establishments):
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

                available = (
                    profile_badge_image is not None and
                    profile_banner_image is not None
                )
                establishment.available = available
                business.available = available
                establishment.save()
                business.save()


            time.sleep(5)
            page += 1
            establishments = IdentityEstablishment.objects.filter(
                available=False
            )[page*count:(page*count) + count]
