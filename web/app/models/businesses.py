from django.db.models import CharField, DateTimeField, Manager
from django.utils.http import urlencode

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
        backend_name = urlencode(name.strip().lower().replace(' ', '-'))
        
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

    backend_name = CharField(max_length=128, primary_key=True)
    
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
        output_array = [
            self.name,
            ' (',
            self.id,
            ')'
        ]
        return ''.join([s for s in output_array])
    
    objects = BusinessManager()
