from django.db.models import Model, Manager, IntegerField, CharField

from knotis.contrib.core.models import KnotisModel
from knotis.contrib.endpoint.models import (
    Endpoint,
    EndpointTypes
)
from knotis.contrib.cassandra.models import ForeignKey


class ContactType:
    EVENTS = 0
    HAPPY_HOUR = 1
    ANNOUNCEMENTS = 2
    OFFERS = 3
    DAILY = 4
    MONTHLY = 5

    CHOICES = (
        (EVENTS, 'Events'),
        (HAPPY_HOUR, 'Happy Hours'),
        (ANNOUNCEMENTS, 'Announcements'),
        (OFFERS, 'Offers'),
        (DAILY, 'Daily'),
        (MONTHLY, 'Monthly')
    )


class ContactManager(Manager):
    def create_contact(
        self,
        contact_type,
        endpoint,
        related_object_id=None,
        custom_context=None
    ):
        return self.create(
            contact_type=contact_type,
            endpoint=endpoint,
            endpoint_type=endpoint.type,
            endpoint_value=endpoint.value.value,
            related_object_id=related_object_id,
            custom_context=custom_context
        )


class Contact(KnotisModel):
    contact_type = IntegerField(
        choices=ContactType.CHOICES,
        null=True,
        db_index=True
    )
    endpoint = ForeignKey(Endpoint)
    endpoint_type = IntegerField(
        choices=EndpointTypes.CHOICES,
        blank=True,
        null=True,
        default=None,
        db_index=True
    )
    endpoint_value = CharField(
        max_length=2048,
        null=True,
        blank=True,
        default=None
    )
    related_object_id = CharField(
        max_length=36,
        blank=True,
        null=True,
        default=None,
        db_index=True
    )
    custom_context = CharField(
        max_length=1024,
        blank=True,
        null=True,
        default=None
    )

    objects = ContactManager()
