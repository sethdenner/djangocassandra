from django.utils.translation import ugettext_lazy as _
#from django.db import models

from quick.models import QuickModel
from quick.fields import QuickCharField, QuickDateTimeField, QuickFloatField, QuickTextField, QuickIntegerField, QuickImageField
# Create your models here.

class RelationTypes:
    UNDEFINED = -1
    NORMAL = 0
    PREMIUM = 1
    PERIODIC = 2

    CHOICES = (
        (UNDEFINED, 'Undefined'),
        (NORMAL, 'Relation'),
        (PREMIUM, 'Premium'),
        (PERIODIC, 'Periodic'),
    )

class Relation(QuickModel):
    relation_type = QuickIntegerField(
        choices=RelationTypes.CHOICES,
        default=RelationTypes.UNDEFINED,
        #null=True,blank=True,
    )

    #user = ForeignKey(User)
    name = QuickCharField(max_length= 80, db_index=True, verbose_name=_("Subject"), required=True)
    description = QuickTextField(verbose_name=_("Relation Body!"), required=True)
    #image = QuickImageField(default="http://placehold.it/200x200/aaa/afa.jpg&text=relation")
    
    class Quick(QuickModel.Quick): 
        exclude = () #('period',)

    def __unicode__(self):
        if (self.name):
            return str(self.name)
        return str(self.id)

    #def save(self, *args, **kwargs): 
    #    if (self.pk):
    #        self.full_clean() 
    #    super(Relation, self).save(*args, **kwargs) 
    #    print "saving relation - type: " + str(self.relation_type)

    """ 
    How do we incorporate many images 
    """
    #Quick = copy.deepcopy(QuickModel.Quick)
    #Quick.exclude = None

class RelationNormal(Relation):
    class Quick(Relation.Quick): 
        exclude = ('relation_type','period')
        filters = {'relation_type': RelationTypes.NORMAL}

    class Meta:
        proxy = True

    def clean(self): 
        print ("what the fuck this even called?")
        self.relation_type = RelationTypes.NORMAL

class RelationPremium(Relation):
    class Meta:
        proxy = True

    class Quick(Relation.Quick): 
        exclude = ('relation_type','period')
        filters = {'relation_type': RelationTypes.PREMIUM}

    def clean(self): 
        print ("premium clean")
        self.relation_type = RelationTypes.PREMIUM

class RelationPeriodic(Relation):
    class Meta:
        proxy = True

    class Quick(Relation.Quick): 
        exclude = ('relation_type',)
        filters = {'relation_type': RelationTypes.PERIODIC}

    def clean(self): 
        self.relation_type = RelationTypes.PERIODIC

