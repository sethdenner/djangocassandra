from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from knotis.contrib.quick.models import QuickModel
from knotis.contrib.quick.fields import (
    QuickCharField,
    QuickDateTimeField,
    QuickFloatField,
    QuickTextField,
    QuickIntegerField,
    QuickImageField,
    QuickForeignKey,
    QuickUUIDField,
    QuickGenericForeignKey,
)

__models__ = ( 'Relation', 'RelationOwner', 'RelationManager', 'RelationEmployee')
__all__ = __models__ + ('IdentityTypes',)

class RelationTypes:
    """ 
        There should be a good way to map type number to the actual type.
        There should be a way to specify the class.
        Types could be inferred from the models list.
    """
    UNDEFINED = -1
    OWNER = 'Owner'
    MANAGER = 'Manager'
    EMPLOYEE = 'Employee'
    FOLLOWING = 'Following'
    LIKES = 'Likes'
    CUSTOMER = 'Customer'
    CONTRIBUTOR = 'Contributor'

    CHOICES = ( 
            (UNDEFINED, UNDEFINED),
            (OWNER, OWNER),
            (MANAGER, MANAGER),
            (EMPLOYEE, EMPLOYEE),
            (FOLLOWING, FOLLOWING),
            (LIKES, LIKES),
            (CUSTOMER, CUSTOMER),
            )

class Relation(QuickModel):
    relation_type = QuickCharField(
        choices=RelationTypes.CHOICES,
        default=RelationTypes.UNDEFINED,
        max_length=25,
    )

    #owner_limit = models.Q(app_label = 'quick', model = 'Identity') | models.Q(app_label = 'auth', model = 'User')
    owner_content_type = QuickForeignKey(ContentType, related_name='relation_owner_set') #, limit_choices_to = owner_limit)
    owner_object_id = QuickUUIDField()
    owner = QuickGenericForeignKey('owner_content_type', 'owner_object_id')

    #subject_limit = models.Q(app_label = 'quick', model = 'Identity') | models.Q(app_label = 'quick', model = 'Product')
    subject_content_type = QuickForeignKey(ContentType, related_name='relation_subject_set') #, limit_choices_to = subject_limit)
    subject_object_id = QuickUUIDField()
    subject = QuickGenericForeignKey('subject_content_type','subject_object_id')

    #user = ForeignKey(User)
    name = QuickCharField(max_length= 80, db_index=True, verbose_name=_("Subject"), required=True)
    description = QuickTextField(verbose_name=_("Relation Body!"), required=True)
    #image = QuickImageField(default="http://placehold.it/200x200/aaa/afa.jpg&text=relation")
    
    class Quick(QuickModel.Quick): 
        exclude = () #('period',)
        #permissions = {'create': self.check_create}
        types = RelationTypes

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

class RelationOwner(Relation):
    class Quick(Relation.Quick): 
        exclude = ('relation_type',)
        filters = {'relation_type': RelationTypes.OWNER}

    class Meta:
        proxy = True

    def clean(self): 
        self.relation_type = RelationTypes.OWNER

class RelationFollowing(Relation):
    class Meta:
        proxy = True

    class Quick(Relation.Quick): 
        exclude = ('relation_type',)
        filters = {'relation_type': RelationTypes.FOLLOWING}

    def clean(self): 
        print ("premium clean")
        self.relation_type = RelationTypes.FOLLOWING

class RelationEmployee(Relation):
    class Meta:
        proxy = True

    class Quick(Relation.Quick): 
        exclude = ('relation_type',)
        filters = {'relation_type': RelationTypes.EMPLOYEE}
        #permissions = { 'create': request.session['identity'].relations_set.filter( relation_type = RelationTypes.OWNER, subject = subject)
        #        }

    def clean(self): 
        self.relation_type = RelationTypes.EMPLOYEE
