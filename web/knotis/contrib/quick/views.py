from knotis.utils.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django import http

import django.db.models as models

from knotis.contrib.quick.util import quick_models
from knotis.contrib.quick.forms import quick_modelform_factory
import knotis.contrib.quick.errors

"""
Same as before except:

    separate functions for:
        get_filters
        get_context
        get_templates
        get_layout
        get_input_format
        get_output_format
        get_method

        render_formatted

    support:
        embeded
        ajax
        raw

    features:
        return raw templates / templates as mustache or ajaxish
"""

class QuickView(View):
    #_allowed_methods = ['get', 'post', 'put', 'delete'] #, 'head', 'options', 'trace'] 
    def get_filters(self):
        self.pk = self.dispatch_kwargs.get('pk',None)
        self.queryset = self.model._default_manager.all()

        if self.pk is not None:
            self.queryset = self.queryset.filter(pk=self.pk)

        #if args match __ attempt to add the filters to the query set...
        self.potential_filters = filter(lambda x: '__' in x, self.request.GET.keys())
        for potential_filter in self.potential_filters:
            # what happens here if __ splits 3 ways? It's invalid but what will the error be?
            split_filter = potential_filter.split('__')
            if (len(split_filter) != 2): continue
            [filter_field, filter_type] = split_filter
            filter_value = request.GET[potential_filter]
            # handle multiple values here i.e. "{pk1, pk2, ...}"

            # check that filter_field is on the model.
            # check that the filter_type is in the supported list.
            filter_list = [ 'exact', 'iexact', 'contains', 'startswith', 'endswith', 'isnull', 'gt', 'lt','in' ]
            if filter_field in model.get_filterable_fields() and (filter_type in filter_list):
                self.queryset = self.queryset.filter( **{potential_filter : filter_value} )
            else:
                raise quick.errors.ExceptionFilterInvalid()

    def get_context(self):
        self.context = { 
                'ModelName': self.model.__name__,
                'layout': self.layout,
                'request': self.request,
                'title': self.model.__name__,
                'template_roots': self.template_roots,
                }

    def get_template_roots(self):
        def get_name(cls):
            if hasattr(cls,'Quick') and hasattr(cls.Quick,'url_name'):
                return cls.Quick.url_name
            return cls.__name__
        import inspect
        #self.template_roots = map(lambda x: get_name(x).lower(), inspect.getmro(self.model))
        self.template_roots = [get_name(x).lower() for x in inspect.getmro(self.model)]
        self.template_roots += ('quickmodel/',)

    def get_templates(self, default_name):
        """
        Only get the template html name from view. Add the root based on trying model first and defaulting to quick.
        """
        view_name = self.request.GET.get('view', default_name)
        template_names = map(lambda x: x + '/' + view_name + '.html', self.template_roots)
        
        #added so models inheriting only from QuickBase work - ugly
        
        print "FIXME: validate view_name before just using it."
        return template_names

    def get_layout(self):
        self.embeded = self.request.GET.get('embeded', False)
        if (self.embeded):
            self.layout = 'embeded.html'
        else:
            self.layout = 'default.html'
        self.layout = self.request.GET.get('layout', self.layout)

    def get_input_format(self):
        mime_format = 'text/html'
        mime_format = self.request.META.get('CONTENT_TYPE', mime_format)
        mime_format = self.request.GET.get('format', mime_format)
        self.input_format = mime_format

    def get_output_format(self):
        pass

    def get_method(self):
        self.method = self.request.method.lower()
        self.method = self.request.GET.get('method', self.method).lower()

    def get(self):
        if (self.pk):
            self.context.update( { 
                'object': self.queryset.get(),
                'ViewName': 'DetailView',
                } )
            self.templates = self.get_templates('DetailView')
        else:
            self.context.update( { 
                'object_list': self.queryset.all(),
                'ViewName': 'ListView',
                } )
            self.templates = self.get_templates('ListView')

    def get_form_class(self, extra=0):
        if hasattr(self.model.Quick, 'form_class'):
            return self.model.Quick.form_class(self.model, extra)

        #from quick.forms import quick_modelform_factory
        #from django.forms.models import model_to_dict 
        #from django.forms.models import modelformset_factory, inlineformset_factory
        #from django.forms.models import formset_factory

        #QuickForm = quick_modelform_factory(self.model)
        #ModelFormSet = modelformset_factory(self.model, form=QuickForm, extra = extra)
        #return ModelFormSet

    def post(self):
        if (self.pk):
            extra = 0
        elif (self.request.GET.has_key('new')):
            new_count = self.request.GET.get('new',1)
            try:
                extra = int(new_count)
            except:
                extra = 1
            #FIXME This isn't the right way to reistrict this.
            self.queryset = self.queryset.none()
        else:
            extra = 0
        extra += int(self.request.GET.get('extra',0))
        
        
        FormClass = self.get_form_class(extra)

        obj = None
        if (self.request.POST):
            if (self.input_format == 'application/json'):
                import json
                # Example from chrome to submit product form.
                # $.ajax({url:"/product/?format=json", success: function(resp) { $("#db").append(resp); }, dataType:'text', type:'post', data: JSON.stringify( $(document.forms[0]).serializeObject() ), contentType:'application/json' });
                values = json.loads(self.request.raw_post_data)
            else: # if html multi part form
                values = self.request.POST.copy()

            form = FormClass(values, self.request.FILES)

            #We don't need to test validity, save what is valid, we'll show any remaining errors...if (form.is_valid()):
            form.save()
        else:
            form = FormClass(queryset=self.queryset)
        
        self.context.update( { 
                'object': obj,
                'form': form,
                'ViewName': 'EditView',
        } )
        self.templates = self.get_templates('EditView')

    def put(self):
        self.post()

    def delete(self):
        print "FIXME: DELETE NOT IMPLEMENTED - set deleted flag and call post"
        self.method_not_allowed()

    def method_not_allowed(self):
        raise Exception("Method not allowed")
        return self.http_method_not_allowed(self.request, self.dispatch_args, self.dispatch_kwargs)

    def dispatch(self, request, model, *args, **kwargs):
        self.request = request
        self.model = model
        self.dispatch_args = args
        self.dispatch_kwargs = kwargs

        self.get_method()

        self.get_input_format()
        
        self.get_layout()

        self.get_filters()
        
        self.get_template_roots()

        self.get_context()

        methods = {'get': self.get, 'post': self.post, 'put': self.put, 'delete': self.delete}

        method = methods.get(self.method, self.method_not_allowed)
        method()

        """
            This section needs to depend on output format and allow for specific handles for each format.
        """
        # IF HTML
        if (self.input_format in ( 'text/html', 'text/plain','application/x-www-form-urlencoded') ) or self.input_format.startswith('multipart/form-data'):
            """
            get the model's specified template rendered inside of the specified layout
            """
            from django.template.response import TemplateResponse
            model_response = TemplateResponse(
                request = self.request,
                template = self.templates,
                context = self.context,
            )
            model_response.render()

            self.context['content'] = model_response.content

            response_class = TemplateResponse
            return response_class(
                request = self.request,
                template = self.layout,
                context = self.context,
            )

        elif (self.input_format in ( 'application/json', 'json')):
            from django.core import serializers
            data = serializers.serialize('json', self.queryset.all())
            return HttpResponse(data, mimetype='application/json')

        return HttpResponse("Mimeformat not found" + self.input_format, mimetype='mime_format')

