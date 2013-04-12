from piston.handler import BaseHandler
from piston.utils import validate, require_mime, rc
from piston.doc import generate_doc
from django.contrib.auth.models import User
from django.core import serializers
from django.shortcuts import render_to_response, get_object_or_404

from knotis.contrib.content.models import Content


class ContentHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    model = Content
    # exclude = ('parent')
    # fields = ('user','group','c_type','value')
    fields = (
        'id',
        # 'parent_id',
        # ('parent', ('value')),
        ('user', ('username', 'id', 'email')),
        'name',
        'content_type',
        'value',
        ('group', ('id', 'name')),
        ('type', ('id', 'name')),
    )

    @classmethod
    def parent_id(self, instance):
        return instance.parent.id

    def read(self, request, content_id=None, template_name=None):
        base = Content.objects
        #latest_content_list = Content.objects.all().order_by('-pub_date')[:5]

        if content_id:
            return base.get(pk=content_id)
        elif template_name:
            return Content.objects.get_template_content(template_name)
        else:
            return base.all()

#    def create(self, request):
#        #if request.content_type:
#        data = request.data
#
#        intance = deserialize(type:'json', data)
#        
#        #em = self.model(title=data['title'], content=data['content'])
#        #value=data['value'])
#        instance = self.model() 
#
#        attrs = self.flatten_dict(data)
#        #for k,v in attrs.iteritems():
#        #    setattr(instance, k, v)
#
#        for k,v in attrs.iteritems():
#            v = new typeof (instance.'k')
#            setattr(instance, k, v)
#        #
#        instance['c_type'] = ContentType(attrs['c_type'])
#        instance['user'] = User(attrs['user'])
#        instance['group'] = Group(attrs['group'])
#
#        instance.save()
#        
#        #for comment in data['comments']:
#        #    Comment(parent=em, content=comment['content']).save()
#            
#        return rc.CREATED
#        #else:
#        #    super(ExpressiveTestModel, self).create(request)
#
#    #@require_mime('json') 
#    #@essential(['id'])
#    #@validate(MyModelForm, 'PUT', ['testfield'], MyModel)
#    #def update(self, request): #, *args, **kwargs):
#    def update(self, request): #, content_id=None):
#        #request.data = request.POST
#        # this test returns true but the data is still stored in the post.
#        if not hasattr(request, "data"):
#            request.data = request.POST
#        try:
#            #instance = base.get(pk='24f285fd-847e-4f95-8efe-9ca510d9a64f') #request.data['id'])
#            #instance = self.queryset(request).get(fqdn=kwargs['mymodel'])
#            instance = get_object_or_404(Content,pk='24f285fd-847e-4f95-8efe-9ca510d9a64f') #request.data['id'])
#        except self.model.DoesNotExist:
#            return rc.NOT_FOUND
#        except self.model.MultipleObjectsReturned:
#            return rc.DUPLICATE_ENTRY
#        except:
#            return rc.BAD_REQUEST
#
#        attrs = self.flatten_dict(request.data)
#        for k,v in attrs.iteritems():
#            setattr(instance, k, v)
#        instance.save()
#        return instance

