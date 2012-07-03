from piston.handler import BaseHandler
from piston.utils import validate, require_mime, rc
from piston.doc import generate_doc
from django.contrib.auth.models import User
from django.core import serializers
from django.shortcuts import render_to_response, get_object_or_404
from app.models.testmodel import TestModel

class TestModelHandler(BaseHandler):
    allowed_methods = ('GET','PUT','POST','DELETE')
    model = TestModel
    #exclude = ('c_parent_id','c_parent','title')
    #fields = ('user','group','c_type','value')
    #fields = ('id',('user',('username','id','email')),'value',('group',('id','name')),('c_type',('id','name')),'value')
    
    def read(self, request, testmodel_id=None):
        base = TestModel.objects
        #latest_content_list = Content.objects.all().order_by('-pub_date')[:5]

        if testmodel_id:
            return base.get(pk=testmodel_id)
        else:
            return base.all()

