from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.shortcuts import get_object_or_404

from knotis.views import ApiView
from knotis.utils.regex import REGEX_UUID

from knotis.contrib.auth.models import KnotisUser
from knotis.contrib.identity.models import (
    Identity,
    IdentityIndividual
)

from models import (
    Relation,
    RelationTypes
)

class RelationApi(object):
    @staticmethod
    def create_following(subject, related):
        relation = Relation.objects.create_following(
            subject,
            related
        )
#       relation.save()
        return relation

    @staticmethod
    def delete_following(subject, related):
        relations = Relation.objects.follows(subject, related)
        for relation in relations:
            relation.delete()
 


class FollowApiView(ApiView):
    api_path = 'relation/follow'

    def get_needed_identities(self, request):
        if request.user.is_authenticated():
            self.subject_id = request.session.get('current_identity')
            self.subject = Identity.objects.get(pk=self.subject_id)

            self.related_id = request.DATA.get('related_id')
            self.related = Identity.objects.get(pk=self.related_id)

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        self.get_needed_identities(request)
        errors = {}

        try:
            RelationApi.create_following(self.subject, self.related)

        except Exception, e:
            logger.exception('failed to follow')
            errors['no-field'] = e.message

        return self.generate_ajax_response({
            'errors': errors,
            'relation': {
                'pk': relation.pk,
                'subject_id': relation.subject_object_id,
                'related_id': relation.related_object_id,
                'description': relation.description
            }
        })

    def delete(
        self,
        request,
        *args,
        **kwargs
    ):
        self.get_needed_identities(request)
        errors = {}
        try:
            RelationApi.delete_following(self.subject, self.related)
        except Exception, e:
            logger.exception('failed to unfollow')
            errors['no-field'] = e.message

        if errors:
            return self.generate_ajax_response({
                'errors': errors,
            })
        else:
            return self.generate_ajax_response({
                'status': 'OK',
            })


class RelationApiView(ApiView):
    api_path = ''.join([
        'relation(/(?P<relation_pk>',
        REGEX_UUID,
        '))?'
    ])

    def get(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        pk = kwargs.get('relation_pk')

        index = int(request.GET.get('i', '0'))
        count = int(request.GET.get('c', '20'))
        relation_type = request.GET.get('relation_type')
        related = request.GET.get('related')
        subject = request.GET.get('subject')

        try:
            relations = Relation.objects.filter(deleted=False)
            if pk:
                relations = relations.filter(pk=pk)

            else:
                if relation_type:
                    relations = relations.filter(relation_type=relation_type)

                if related:
                    relations = relations.filter(related_object_id=related)

                if subject:
                    relations = relations.filter(subject_object_id=subject)

            if index:
                relations = relations[index:index + count]

            else:
                relations = relations[:count]

        except Exception, e:
            logger.exception('failed to filter relations')
            errors['no-field'] = e.message
            relations = None

        relation_data = {}
        if relations:
            for relation in relations:
                relation_data[relation.pk] = {
                    'relation_type': relation.relation_type,
                    'subject': relation.subject_object_id,
                    'related': relation.related_object_id,
                    'description': relation.description
                }

        return self.generate_ajax_response({
            'errors': errors,
            'relations': relation_data
        })

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        pk = kwargs.get('relation_pk')

        instance = None
        if pk:
            try:
                instance = Relation.objects.get(pk=pk)

            except Relation.DoesNotExist:
                pass

            except Exception, e:
                logger.exception()
                raise e

        relation_type = request.POST.get('relation_type')

        if (
            RelationTypes.INDIVIDUAL == relation_type or
            RelationTypes.SUPERUSER == relation_type
        ):
            subject_type = KnotisUser
            related_type = IdentityIndividual

        else:
            subject_type = Identity
            related_type = Identity

        subject_pk = request.POST.get('subject')
        related_pk = request.POST.get('related')

        subject = subject_type.objects.get(pk=subject_pk)
        related = related_type.objects.get(pk=related_pk)

        relation = Relation.objects.create(
            relation_type=relation_type,
            subject=subject,
            related=related
        )

        if relation:
            relation_data = {
                'id': relation.id,
                'subject': relation.subject_object_id,
                'related': relation.related_object_id,
                'description': relation.description
            }

        else:
            relation_data = None

        return self.generate_ajax_response({
            'relation': relation_data,
        })

    def delete(
        self,
        request,
        *args,
        **kwargs
    ):
        relation_pk = kwargs.get('relation_pk', None)
        relation = get_object_or_404(Relation, pk=relation_pk)
        relation.deleted = True
        relation.save()

        return self.generate_ajax_response({
            'relation_id': relation_pk,
            'deleted': relation.deleted
        })
