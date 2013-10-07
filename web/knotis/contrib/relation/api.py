from django.utils.log import logging
logger = logging.getLogger(__name__)

from knotis.views import ApiView

from models import Relation

from forms import RelationForm
from knotis.contrib.identity.models import Identity

class FollowApi(ApiView):
    model = Relation
    api_url = 'follow'

    def post(
        self,
        request,
        *args,
        **kwargs
    ):

        errors = {}

        try:
            if request.user.is_authenticated():
                subject_id = request.session.get('current_identity_id')
                subject = Identity.objects.get(pk=subject_id)
                
                related_id = request.REQUEST.get('related_id')
                related = Identity.objects.get(pk=related_id)

                verb = request.REQUEST.get('verb')

                if verb == 'follow':
                    Relation.objects.create_following(
                        subject,
                        related
                    ).save()

                elif verb == 'unfollow':
                    follows = Relation.objects.get_following(subject)
                    for follow in follows:
                        if not follow.deleted and (follow.related == related):
                            follow.deleted = True
                            follow.save()
                        
        except Exception, e:
            logger.exception('failed to follow')
            errors['no-field'] = e.message
            
        return self.generate_response({
            'errors': errors
        })

class RelationApi(ApiView):
    model = Relation
    api_url = 'relation'

    def get(
        self,
        request,
        *args,
        **kwrags
    ):
        errors = {}

        index = int(request.GET.get('i', '0'))
        count = int(request.GET.get('c', '20'))
        pk = request.GET.get('pk')
        relation_type = request.GET.get('relation_type')
        related_id = request.GET.get('related_id')
        subject_id = request.GET.get('subject_id')

        try:
            relations = Relation.objects.all()
            if pk:
                relations = relations.filter(pk=pk)

            if relation_type:
                relations = relations.filter(relation_type=relation_type)

            if related_id:
                relations = relations.filter(related_object_id=related_id)

            if subject_id:
                relations = relations.filter(subject_object_id=subject_id)

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
                relation_data[relation.id] = {
                    'relation_type': relation.relation_type,
                    'subject_id': relation.subject_object_id,
                    'related_id': relation.related_object_id,
                    'description': relation.description
                }

        return self.generate_response({
            'errors': errors,
            'relations': relation_data
        })

    def post(
        self,
        request,
        *args,
        **kwargs
    ):
        errors = {}

        form = RelationForm(data=request.POST)

        instance = None

        if form.is_valid():
            try:
                instance = form.save()

            except Exception, e:
                logger.exception(
                    'an exception occurred during relation creation'
                )
                errors['no-field'] = e.message

        else:
            for field, messages in form.errors.iteritems():
                errors[field] = [message for message in messages]

        if instance:
            instance_data = {
                'id': instance.id,
                'subject': instance.subject_object_id,
                'related': instance.related_object_id,
                'description': instance.description
            }

        else:
            instance_data = None

        return self.generate_response({
            'relation': instance_data,
            'errors': errors
        })
