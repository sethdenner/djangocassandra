from knotis.contrib.auth.models import (
    KnotisUser,
    UserInformation
)
from knotis.contrib.relation.models import (
    Relation,
    RelationTypes
)
from knotis.contrib.identity.models import (
    Identity,
    IdentityIndividual,
    IdentityBusiness,
    IdentityEstablishment,
    IdentityTypes
)

from django.contrib.contenttypes.models import ContentType


def reset_user(user):
    identities = set()
    user_content_type = ContentType.objects.get_for_model(user)
    user_identity_relation = Relation.objects.get(
        subject_content_type__pk=user_content_type.id,
        subject_object_id=user.id
    )
    user_identity = user_identity_relation.related

    identity_content_type = ContentType.objects.get_for_model(
        user_identity
    )
    identity_relations = Relation.objects.filter(
        relation_type=RelationTypes.MANAGER,
        subject_content_type__pk=identity_content_type.id,
        subject_object_id=user_identity.id,
        related_content_type=identity_content_type.id
    )
    for relation in identity_relations:
        identities.add(relation.related)

    user_identity.name = IdentityIndividual.DEFAULT_NAME
    user_identity.save()

    for identity in identities:
        identity.delete()

    for relation in identity_relations:
        relation.delete()
