from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms import layout 

from string import Template
from django.utils.safestring import mark_safe
import knotis.contrib.quick as quick


"""
This file contains logic that:

    Allow for extending model forms with the Meta field on models.
    
    Creates a customized ModelForm with:
        the ability to save even if there are Form Errors.
        an included Helper object to customize the form.

    A model form factory that 


"""
"""
Solution for extending forms via model meta attributes.
http://blog.brendel.com/2012/01/django-modelforms-setting-any-field.html
"""
class ExtendedMetaModelForm(forms.ModelForm):
    """
    Allow the setting of any field attributes via the Meta class.
    """
    def __init__(self, *args, **kwargs):
        """
        Iterate over fields, set attributes from Meta.field_args.
        """
        super(ExtendedMetaModelForm, self).__init__(*args, **kwargs)
        if hasattr(self.Meta, "field_args"):
            # Look at the field_args Meta class attribute to get
            # any (additional) attributes we should set for a field.
            field_args = self.Meta.field_args
            # Iterate over all fields...
            for fname, field in self.fields.items():
                # Check if we have something for that field in field_args
                fargs = field_args.get(fname)
                if fargs:
                    # Iterate over all attributes for a field that we
                    # have specified in field_args
                    for attr_name, attr_val in fargs.items():
                        if attr_name.startswith("+"):
                            merge_attempt = True
                            attr_name = attr_name[1:]
                        else:
                            merge_attempt = False
                        orig_attr_val = getattr(field, attr_name, None)
                        if orig_attr_val and merge_attempt and \
                                    type(orig_attr_val) == dict and \
                                    type(attr_val) == dict:
                            # Merge dictionaries together
                            orig_attr_val.update(attr_val)
                        else:
                            # Replace existing attribute
                            setattr(field, attr_name, attr_val)

class QuickModelForm(ExtendedMetaModelForm):
    def __init__(self, *args, **kwargs):
        super(QuickModelForm, self).__init__(*args, **kwargs)
        model = self.Meta.model #Product
        self.helper = FormHelper()
        self.helper.form_id = 'id_' + model.__name__
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        #self.helper.form_style = 'inline'
        self.helper.layout = layout.Layout(layout.HTML("{%if not forloop.first %}</div>{% endif %}<div class='well wookmarkbox'><a href='/" + model.__name__.lower() + "/{{ actual_form.id.value }}/'>View:{{ actual_form.id.value }}</a>"))

        #self.helper.form_tag = False
        #FIXME use reverse_lazy -- but right now that's broken because I'm using or's in my regexes.
        # works single values -- self.helper.form_action = "/" + str(model.__name__).lower() + "/" + str(self.instance.pk) + "/?method=put"
        # self.helper.form_action = "/" + str(model.__name__).lower() + "/?method=put"# + str(self.instance.pk) + "/?method=put"
        #'/quick/' + model.__name__ + 'CreateView'
        #FIX ME - only set this enc type if we have image fields.
        self.helper.enctype="multipart/form-data"
        self.helper.add_input(layout.Submit('submit', 'Submit'))

    def validate(self, *args, **kwargs):
        new_type = request.POST[model.Quick.type_name] 
        new_model = self.model.Quick.types.CLASSES[new_type]

        self.model.Quick.permissions['create'](*args, **kwargs)

    def save(self, commit=True):
        if self.instance.pk is None:
            fail_message = 'created'
        else:
            fail_message = 'changed'

        errors = self.errors
        exclude = None
        if (errors):
            exclude = self.errors.keys()
            self._errors = dict()
            completed = False
        else:
            completed = True

        from django.forms.models import save_instance
        save_instance(self, self.instance, self._meta.fields,
                             fail_message, commit=False, exclude=exclude, construct=False)

        for field in self.instance._meta.fields:
            if (isinstance(field, quick.fields.QuickField) and field.required):
                if (not getattr(self.instance, field.name)):
                    errors[field.name]="Required"
        
        if (errors):
            completed = False
        else:
            completed = True
        self.instance.completed = completed

        self.instance.save()
        self.save_m2m()

        # Had this in clean, but it wasn't working because the file hadn't been written to disk yet.
        for field in self.instance._meta.fields:
            if (isinstance(field, quick.fields.QuickImageField)):
                print "FIXME - This is ASS UGLY - but needed or images don't get their correct image url on upload."
                self.files[self.prefix + "-" + field.name] = getattr(self.instance, field.name)

        """ Update form data to reflect changes made during saving. """
        #self.data['completed'] = completed
        
        # works with id but trying pk.
        if (hasattr(self.instance,'id')):
            self.data[self.prefix + "-id"] = getattr(self.instance, 'id')
            self.id = id
            setattr(self, '_changed_data', self.changed_data + ['id','completed'])
        #self.data[self.prefix + "-pk"] = getattr(self.instance, 'pk')
        #self.pk = pk
        #setattr(self, '_changed_data', self.changed_data + ['pk','completed'])

        print "changed data: " + str(self.changed_data)
        #print "id: " + str(self.instance.id)

        """ Put back any errors so they get rendered. """
        if errors:
            self._errors = errors


    def clean(self):
        data = super(QuickModelForm, self).clean()
        #data['completed'] = self.instance.completed 
        #FIXME: This should be abstracted -- QuickForms should not REQUIRE a copmeleted attribute.
        if (hasattr(self.instance, 'completed')):
            self.data[self.prefix+'-completed'] = self.instance.completed

        print "cleaning form"
        #print self.data
        #print dir(self)
        #print self.auto_id
        #print "is bound?" + str( self.is_bound )
        #print self.prefix
        #print "done cleaning form"
        return data

    def full_clean(self):
        """
        Cleans all of self.data and populates self._errors and
        self.cleaned_data.
        """
        from django.forms.util import ErrorDict
        self._errors = ErrorDict()
        if not self.is_bound: # Stop further processing.
            return
        self.cleaned_data = {}
        # If the form is permitted to be empty, and none of the form data has
        # changed from the initial data, short circuit any validation.
        if self.empty_permitted and not self.has_changed():
            return
        self._clean_fields()
        self._clean_form()
        self._post_clean()

def quick_modelform_factory(model, form=QuickModelForm, fields=None, exclude=(),
                      formfield_callback=None,  widgets={}):
    
    exclude += model.Quick.exclude

    from django.forms import models as model_forms
    # 1.4 only
    #return model_forms.modelform_factory(model, QuickModelForm, fields, exclude, formfield_callback, widgets)

    # 1.3
    modelform = model_forms.modelform_factory(model, form, fields, exclude, formfield_callback)
    modelform.Meta.widgets = widgets
    return modelform

"""
Later for uploading images
"""

class PrettyFileInput(forms.ClearableFileInput):
    def render(self, name, value, attrs=None):
#        tpl = Template(u"""
#<div class="fileupload fileupload-new" data-provides="fileupload">
#  <span class="btn btn-file"><span class="fileupload-new">Select file</span><span class="fileupload-exists">Change</span><input type="file" /></span>
#  <span class="fileupload-preview"></span>
#  <a href="#" class="close fileupload-exists" data-dismiss="fileupload" style="float: none">x</a> </div>
#""")
#        return mark_safe(tpl.substitute(colour=value))
        image_url = str(value)

        #FIXME -- handle local vs remote urls...
        if image_url:
            if (not image_url[:4] == "http"):
                from django.conf import settings
                image_url = settings.MEDIA_URL + image_url
        else:
            image_url = "http://www.placehold.it/100x75/EFEFEF/AAAAAA&text=no+image"

        tpl = Template(u"""
<div class="fileupload fileupload-new" data-provides="fileupload">
  <div class="fileupload-new thumbnail" style="width: 100px; height: 75px;"><img src='""" + image_url + """' /></div>
  <div class="fileupload-preview fileupload-exists thumbnail" style="max-width: 100px; max-height: 75px; line-height: 20px;"></div>
  <div>
    <span class="btn btn-file"><span class="fileupload-new">Select image</span><span class="fileupload-exists">Change</span>
        <input type="file" name="$name" id="$id"/>
    </span>
    <a href="#" class="btn fileupload-exists" data-dismiss="fileupload">Remove</a>
  </div>
</div>
""")
        return mark_safe(tpl.substitute(name=name, id="id_" + name))



#class QuickForm(forms.ModelForm):
#    class Meta:
#        model = ImageUpload2
#        #widgets = { 
#        #    'imagefile': PrettyFileInput()
#        #}   
#
#    def __init__(self, *args, **kwargs):
#        self.helper = FormHelper()
#        self.helper.form_id = 'id_imageupload2_crispyadd'
#        self.helper.form_class = 'blueForms'
#        self.helper.form_method = 'post'
#        self.helper.form_action = 'imageupload2_crispyadd'
#        self.helper.enctype="multipart/form-data"
#
#        self.helper.add_input(Submit('submit', 'Submit'))
#
#        super(ImageUpload2Form, self).__init__(*args, **kwargs)

#class ImageUpload2Form(forms.ModelForm):
#    class Meta:
#        model = ImageUpload2
#        widgets = { 
#            'imagefile': PrettyFileInput()
#        }   
#    def __init__(self, *args, **kwargs):
#        self.helper = FormHelper()
#        self.helper.form_id = 'id_imageupload2_crispyadd'
#        self.helper.form_class = 'blueForms'
#        self.helper.form_method = 'post'
#        self.helper.form_action = 'imageupload2_crispyadd'
#        self.helper.enctype="multipart/form-data"
#
#        self.helper.add_input(Submit('submit', 'Submit'))
#
#        super(ImageUpload2Form, self).__init__(*args, **kwargs)
