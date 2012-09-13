#from app.models.contents import Content

import getpass

import MySQLdb
import MySQLdb.cursors
import hashlib
from knotis_auth.models import User
from app.models.businesses import BusinessManager, Business
from app.models.offers import OfferManager
from app.models.cities import CityManager, City
from app.models.categories import CategoryManager, Category
from app.models.endpoints import EndpointEmail, EndpointTypes

from app.models.neighborhoods import NeighborhoodManager, Neighborhood

from legacy.models import BusinessIdMap

"""
TODO:
    Add suport for:
        * salt
        * prehashed passwords
        * facebook_id
        * twitter_id
        * follow new deals, service announcements, events
"""

#     import user
def import_user(cursor):
    print 'IMPORTING USERS!'
    cursor.execute("""SELECT * from users;""")

    all_users = cursor.fetchall()

    for user_table in all_users:

        email = user_table['email']
        first_name = user_table['firstName']
        last_name = user_table['lastName']
        password = user_table['email']

        print 'Importing user %s' % email

        user, account_type  = User.objects.create_user(
            first_name,
            last_name,
            email,
            password
        )

        endpoint_email = EndpointEmail.objects.create_endpoint(
            user,
            EndpointTypes.EMAIL,
            email,
            primary=True
        )

# TODO: sebastian

#     import business
def import_business(cursor):

    cursor.execute("""SELECT * from merchantProfile""")

    all_businesses = cursor.fetchall()
    for business_table in all_businesses:
        name        = business_table['name'].decode('cp1252')
        description = business_table['description'].decode('cp1252')
        phone       = business_table['phone']
        summary     = business_table['extendedDescription'].decode('cp1252')

        address     = business_table['street1'] + business_table['street2']
        twitter_name= business_table['twitter']
        facebook_uri= business_table['facebook']
        yelp_id     = business_table['yelp']

        # Getting the user id for the new system.
        old_user_id     = business_table['userId']
        if old_user_id == 0:
            continue
        cursor.execute("""SELECT email FROM users WHERE id = '%s'""" % old_user_id)
        username = cursor.fetchone()
        print 'Importing business for %s with %s' % (name ,username)
        if username == None:
            print "USER %s NOT IN SYSTEM." % old_user_id
            continue
            #raise

        username = username['email'].decode('cp1252')
        user = User.objects.get(username=username)

        business_manager = BusinessManager()
        new_business = business_manager.create_business(
            user,
            name,
            summary,
            description,
            address,
            phone,
            twitter_name,
            facebook_uri,
            yelp_id
        )

        id = business_table['id']
        BusinessIdMap.objects.create(
            old_id=id,
            new_business=new_business
            )

#     import deal
def import_offer(cursor):
    cursor.execute("""SELECT * from deal""")
    all_offers = cursor.fetchall()
    for old_offer in all_offers:

        # Getting the user id for the new system.
        old_user_id     = old_offer['usersId']
        cursor.execute("""SELECT email FROM users WHERE id = '%s'""" % old_user_id)
        username = cursor.fetchone()

        if username == None:
            print "USER %s NOT IN SYSTEM." % old_user_id
            raise

        username = username['email'].decode('cp1252')
        user = User.objects.get(username=username)

        # Get the business for the new system.
        old_business_id = old_offer['merchantId']
        #cursor.execute("""SELECT name FROM merchantProfile WHERE id = '%s'""" % old_business_id)

        #business_name = cursor.fetchone()
        #if business_name == None:
        #    print "BUSINESS %s NOT IN SYSTEM." % old_business_id
        #    raise

        #business_name = business_name['name']

        #business = Business.objects.get(business_name=business_name)

        business = BusinessIdMap.objects.get(old_id = old_business_id).new_business
        #business = Business.objects.get(user=user)

        title       = old_offer['title'].decode('cp1252')
        title_type  = old_offer['titleType']
        description = old_offer['description'].decode('cp1252')
        restrictions= old_offer['extendedDescription'].decode('cp1252')


        # Get city instance.
        city_id     = old_offer['cityId']
        c.execute("""select title from city where id=%s""" % city_id)
        city_name = c.fetchone()
        city = None
        if city_name == None:
            #print 'CITY OF ID %s NOT IN DATABASE!' % city_id
            None

        else:

            city_name = city_name['title'].decode('cp1252')

            all_cities = City.objects.all()
            for curr_city in all_cities:
                if curr_city.name.value == city_name:
                    city = curr_city
                    break

        # Address field.
        address     = old_offer['address'].decode('cp1252')

        # Get neighborhood instance.
        neighborhood_id = old_offer['neightbourhoodId']
        c.execute("""select title from neighbourhood where id = %s""" % neighborhood_id)

        neighborhood_name = c.fetchone()
        neighborhood = None

        if neighborhood_name == None:
            #print 'NEIGHBORHOOD with id %s NOT IN DATABASE' % neighborhood_id
            None
        else:
            neighborhood_name = neighborhood_name['title'].decode('cp1252')
            all_neighborhoods = Neighborhood.objects.all()
            for curr_neighborhood in all_neighborhoods:
                if curr_neighborhood.name.value == neighborhood_name:
                    neighborhood = curr_neighborhood
                    break

        image           = old_offer['image']

        # Get the category instance.
        category_id     = old_offer['categoryId']
        c.execute("""select title from category where id = %s""" % category_id)
        category_name = c.fetchone()
        category = None
        if category_name == None:
            print "Category of id %s not in database." % category_id

        else:
            category_name = category_name['title'].decode('cp1252')
            for curr_category in Category.objects.all():
                if curr_category.name.value == category_name:
                    category = curr_category
                    break

        price_retail    = old_offer['oldprice']
        price_discount  = old_offer['newprice']
        start_date      = old_offer['startDate']
        end_date        = old_offer['endDate']
        stock           = old_offer['stock']
        unlimited       = old_offer['unlimited']
        published       = old_offer['Published']

        print 'Importing offer for business %s by user %s' % (business, user)
        new_offer = OfferManager()
        new_offer.create_offer(
            user,
            business,
            title,
            title_type,
            description,
            restrictions,
            city,
            neighborhood,
            address,
            image,
            category,
            price_retail,
            price_discount,
            start_date,
            end_date,
            stock,
            unlimited,
            published
        )

#     import qrcodes
def import_qrcodes(cursor):
    None

def import_categories(cursor):
    cursor.execute("""select * from category""")
    all_categories = cursor.fetchall()
    user = User.objects.get(username='simlay')
    for category_dict in all_categories:
        name = category_dict['title']
        category_manager = CategoryManager()
        print 'Importing category %s by %s' % (name, user)
        category_manager.create_category(user, name)




def import_cities(cursor):
    cursor.execute("""select * from city;""")
    user = User.objects.get(username='simlay')
    all_cities = cursor.fetchall()
    for city_dict in all_cities:
        city_name = city_dict['title']

        new_city = CityManager()

        new_city = new_city.create_city(user=user, name=city_name)

        print 'City %s added by %s' % (new_city, user)

def import_neighborhoods(cursor):
    cursor.execute("""select * from neighbourhood""")
    all_neighborhoods = cursor.fetchall()
    for neighborhood_dict in all_neighborhoods:

        title = neighborhood_dict['title']
        city_id = neighborhood_dict['cityId']
        cursor.execute("""select * from city where id = %s""", city_id)

        city_name = c.fetchone()
        city = None
        if city_name == None:
            #print 'CITY OF ID %s NOT IN DATABASE!' % city_id
            None

        else:

            city_name = city_name['title'].decode('cp1252')

            all_cities = City.objects.all()
            for curr_city in all_cities:
                if curr_city.name.value == city_name:
                    city = curr_city
                    break

        name = title
        user = User.objects.get(username='simlay')
        print "%s creating neighborhood %s in %s" % (user, name, city_name)
        neighborhood_manager = NeighborhoodManager()
        neighborhood_manager.create_neighborhood(
            user,
            city,
            name
        )


if __name__ == '__main__':
    #host = options['host']
    host = '216.70.69.66'

    #user = options['user']
    user = 'cHAsTE2r'

    #sqlDB = options['db']
    sqlDB = 'mclean_knotis'

    #password = getpass.getpass('Enter password:')
    password = 'pHUb9ge4'

    try:
        db = MySQLdb.connect(host=host,
                             user = user,
                             passwd=password,
                             db=sqlDB,
                             cursorclass=MySQLdb.cursors.DictCursor,
                             )

    except:
        print 'Database connect error!'
        import sys
        sys.exit(1)

    c = db.cursor()
    print 'Migration Script!'

    # import os
    # os.system('./reset.sh')

    import_user(c)
    import_business(c)
    import_cities(c)
    import_neighborhoods(c)
    import_categories(c)
    import_offer(c)
