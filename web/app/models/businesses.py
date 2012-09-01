from django.db.models import CharField, DateTimeField, Manager
from django.utils.http import urlquote
from django.contrib.auth.models import User as DjangoUser
from foreignkeynonrel.models import ForeignKeyNonRel

from app.models.knotis import KnotisModel
#from app.models.fields.permissions import PermissionsField
from app.models.contents import Content
from app.models.endpoints import EndpointPhone, EndpointAddress, \
    EndpointTwitter, EndpointFacebook, EndpointYelp
    

class BusinessManager(Manager):
    def create_business(
        self,
        user,
        name,
        summary,
        description,
        address,
        phone,
        twitter_name,
        facebook_uri,
        yelp_id
    ):
        backend_name = urlquote(name.strip().lower().replace(' ', '-'))
        
        content_root = Content(
            content_type='3.0',
            user=user,
            name=backend_name
        )
        content_root.save()
        
        content_business_name = Content(
            content_type='3.1',
            user=user,
            name=backend_name + '_name',
            parent=content_root,
            value=name
        )
        content_business_name.save()
        
        content_summary = Content(
            content_type='3.2',
            user=user,
            name=backend_name + '_summary',
            parent=content_root,
            value=summary
        )
        content_summary.save()
        
        content_description = Content(
            content_type='3.4',
            user=user,
            name=backend_name + '_description',
            parent=content_root,
            value=description
        )
        content_description.save()
        
        endpoint_address = EndpointAddress(
            user=user,
            value=address
        )
        endpoint_address.save()
        
        endpoint_phone = EndpointPhone(
            user=user,
            value=phone
        )
        endpoint_phone.save()
        
        endpoint_twitter = EndpointTwitter(
            user=user,
            value=twitter_name
        )
        endpoint_twitter.save()
        
        endpoint_facebook = EndpointFacebook(
            user=user,
            value=facebook_uri
        )
        endpoint_facebook.save()
        
        endpoint_yelp = EndpointYelp(
            user=user,
            value=yelp_id
        )
        endpoint_yelp.save()
        
        new_business = Business(
            user=user,
            backend_name=backend_name,
            content_root=content_root,
            business_name=content_business_name,
            summary=content_summary,
            description=content_description,
            address=endpoint_address,
            phone=endpoint_phone,
            twitter_name=endpoint_twitter,
            facebook_uri=endpoint_facebook,
            yelp_id=endpoint_yelp
        )
        new_business.save()
        
        return new_business


class Business(KnotisModel):
    class Meta(KnotisModel.Meta):
        verbose_name = "Business"
        verbose_name_plural = 'Businesses'

    backend_name = CharField(max_length=128, db_index=True)

    user = ForeignKeyNonRel(DjangoUser)
    content_root = ForeignKeyNonRel(Content, related_name='business_content_root')
    business_name = ForeignKeyNonRel(Content, related_name='business_business_name')
    summary = ForeignKeyNonRel(Content, related_name='business_summary')
    description = ForeignKeyNonRel(Content, related_name='business_description')
    
    address = ForeignKeyNonRel(EndpointAddress)
    phone = ForeignKeyNonRel(EndpointPhone)
    
    twitter_name = ForeignKeyNonRel(EndpointTwitter)
    facebook_uri = ForeignKeyNonRel(EndpointFacebook)
    yelp_id = ForeignKeyNonRel(EndpointYelp)

    pub_date = DateTimeField('date published', auto_now_add=True)

    def __unicode__(self):
        return self.backend_name
        """
        output_array = [
            self.backend_name,
            ' (',
            self.user.id,
            ')'
        ]
        return ''.join([s for s in output_array])
        """
        
    objects = BusinessManager()
    
    def update(
        self,
        name=None,
        summary=None,
        description=None,
        address=None,
        phone=None,
        twitter_name=None,
        facebook_uri=None,
        yelp_id=None
    ):
        backend_name = None
        if name != self.business_name.value:
            backend_name = urlquote(name.strip().lower().replace(' ', '-'))
            self.backend_name = backend_name
            self.business_name.value = name
            self.business_name.name = backend_name + '_name'
            self.business_name.save()
            self.content_root.name = backend_name
            self.content_root.save()
            
        if summary != self.summary.value or backend_name:
            self.summary.value = summary if summary else self.summary.value
            self.summary.name = backend_name + '_summary' if backend_name else self.summary.name
            self.summary.save()
            
        if description != self.description.value or backend_name:
            self.description.value = description if description else self.description.value
            self.description.name = backend_name + '_description' if backend_name else self.summary.name
            self.description.save()
            
        if address != self.address.value.value:
            self.address.value.value = address
            self.address.value.save()
            
        if phone != self.phone.value.value:
            self.phone.value.value = phone
            self.phone.value.save()
            
        if twitter_name != self.twitter_name.value.value:
            self.twitter_name.value.value = twitter_name
            self.twitter_name.value.save()

        if facebook_uri != self.twitter_name.value.value:
            self.facebook_uri.value.value = facebook_uri
            self.facebook_uri.value.save()
            
        if yelp_id != self.yelp_id.value.value:
            self.yelp_id.value.value = yelp_id
            self.yelp_id.value.save()

        self.save()
