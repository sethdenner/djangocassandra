#from app.models.contents import Content

import getpass

import MySQLdb
import MySQLdb.cursors
import hashlib
from knotis_auth.models import User, AccountTypes
from app.models.businesses import Business, BusinessLink, BusinessSubscription
from app.models.offers import Offer
from app.models.cities import City
from app.models.qrcodes import Qrcode
from app.models.categories import Category
from app.models.transactions import Transaction, TransactionTypes
from app.models.endpoints import EndpointEmail, EndpointTypes

import datetime
import sys

from app.models.neighborhoods import Neighborhood

from legacy.models import BusinessIdMap, OfferIdMap

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
    cursor.execute("""SELECT * from users, users_to_roles WHERE users_to_roles.user_id = users.id ORDER BY email;""")

    all_users = cursor.fetchall()
    added_users = {}

    for user_table in all_users:

        email = user_table['email'].decode('cp1252')

        first_name = user_table['firstName'].decode('cp1252')
        last_name = user_table['lastName'].decode('cp1252')

        password    = user_table['password']
        salt        = user_table['salt']

        account_type = AccountTypes.USER
        role = user_table['role_id']
        if role == 2:
            account_type = AccountTypes.BUSINESS_FREE

        current_users = User.objects.filter(username = email)
        if len(current_users) > 0:
            print 'User %s is already in the database.' % email
            continue

        print 'Importing user %s' % email

        user, account_type  = User.objects.create_user(
            first_name,
            last_name,
            email,
            'whatever nuke in next statement',
            account_type = account_type
        )
        user.password = '$'.join([
            'sha1',
            salt,
            password
        ])
        user.save()

        EndpointEmail.objects.create_endpoint(
            user,
            EndpointTypes.EMAIL,
            email,
            primary=True
        )

# TODO: sebastian

#     import business
def import_business(cursor):

    cursor.execute("""SELECT * FROM merchantProfile, users WHERE users.id = merchantProfile.userId""")

    all_businesses = cursor.fetchall()
    for business_table in all_businesses:
        name        = business_table['name'].decode('cp1252')
        description = business_table['description'].decode('cp1252')
        phone       = business_table['phone'].decode('cp1252')
        summary     = business_table['extendedDescription'].decode('cp1252')

        address     = business_table['street1'].decode('cp1252') + business_table['street2'].decode('cp1252')
        twitter_name= business_table['twitter'].decode('cp1252')
        facebook_uri= business_table['facebook'].decode('cp1252')
        yelp_id     = business_table['yelp'].decode('cp1252')

        # Getting the user id for the new system.
        old_user_id     = business_table['userId']
        if old_user_id == 0:
            continue

        #user = get_user_from_old_id(old_user_id, cursor)
        username = business_table['email'].decode('cp1252')

        user = None
        user_objects = User.objects.filter(username=username)
        if len(user_objects) > 0:
            user = user_objects[0]

        print 'Importing business for %s with username = %s' % (name, username)
        new_business = Business.objects.create_business(
            user,
            name,
            summary,
            description,
            address,
            phone,
            twitter_name,
            facebook_uri,
            yelp_id)

        id = business_table['id']
        BusinessIdMap.objects.create(
            old_id=id,
            new_business=new_business
            )

#     import deal
def import_offer(cursor):
    cursor.execute("""SELECT * from deal, users where users.id = deal.usersId""")
    all_offers = cursor.fetchall()
    for old_offer in all_offers:

        # Getting the user id for the new system.
        #old_user_id     = old_offer['usersId']
        username = old_offer['email'].decode('cp1252')
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

        business = None
        businesses = BusinessIdMap.objects.filter(old_id = old_business_id)
        if len(businesses) > 0:
            business = businesses[0].new_business

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
        premium         = old_offer['premium']
        active          = old_offer['active']
        end_date        = old_offer['endDate']

        if end_date <= datetime.datetime.now():
            active = 0

        print 'Importing offer for business %s by user %s' % (business, user)
        new_offer = Offer.objects.create_offer(
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
            active
        )

        old_offer_id = old_offer['id']

        OfferIdMap.objects.create(
            old_id=old_offer_id,
            new_offer = new_offer
            )


def import_categories(cursor):
    cursor.execute("""select * from category""")
    all_categories = cursor.fetchall()
    user = User.objects.get(username='simlay')
    for category_dict in all_categories:
        name = category_dict['title'].decode('cp1252')
        print 'Importing category %s by %s' % (name, user)
        category = Category.objects.create_category(user, name)


def import_cities(cursor):
    cursor.execute("""select * from city;""")
    user = User.objects.get(username='simlay')
    all_cities = cursor.fetchall()
    for city_dict in all_cities:
        city_name = city_dict['title'].decode('cp1252')

        new_city = City.objects.create_city(user=user, name=city_name)

        print 'City %s added by %s' % (city_name, user)

def import_neighborhoods(cursor):
    cursor.execute("""select * from neighbourhood""")
    all_neighborhoods = cursor.fetchall()
    for neighborhood_dict in all_neighborhoods:

        title = neighborhood_dict['title'].decode('cp1252')
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
        Neighborhood.objects.create_neighborhood(
            user,
            city,
            name
        )

#     import qrcodes
def import_qrcodes(cursor):

    cursor.execute("""select * from qrcodeHistory""")
    all_qrcodes = cursor.fetchall()
    for qrcode_dict in all_qrcodes:

        old_business_id = qrcode_dict['merchantId']
        uri             = qrcode_dict['link'].decode('cp1252')

        qrcode_type     = qrcode_dict['qrcodeType']
        qrcode_date     = qrcode_dict['date']
        print 'Importing qrcode: old_business_id = %s, qrcode_type = %s, uri = %s, qrcode_date = %s' \
            % (old_business_id, qrcode_type, uri, qrcode_date)

        businesses = BusinessIdMap.objects.filter(old_id = old_business_id)
        business = None
        if len(businesses) > 0:
            business = businesses[0].new_business

        new_qrcode = Qrcode(
                business = business,
                uri      = uri,
                qrcode_type = qrcode_type,
                )
        new_qrcode.save()


def import_business_links(cursor):
    cursor.execute('''select * from merchantLinks''')
    all_links = cursor.fetchall()
    for link_table in all_links:
        old_business_id = link_table['merchantId']
        uri             = link_table['urlLink'].decode('cp1252')
        title           = link_table['titleLink'].decode('cp1252')

        businesses = BusinessIdMap.objects.filter(old_id = old_business_id)
        business = None
        if len(businesses) > 0:
            business = businesses[0].new_business
        print 'Importing business link for %s to %s' % (business, uri)
        new_business_link = BusinessLink(
                business = business,
                uri = uri,
                title = title,
                )
        new_business_link.save()

def import_transactions(cursor):
    cursor.execute('''select * from dealOrder,users where users.id = dealOrder.accountId''')
    all_transactions = cursor.fetchall()
    for transaction_table in all_transactions:
        account_id  = transaction_table['accountId']
        username = transaction_table['email'].decode('cp1252')
        user = User.objects.get(username=username)

        deal_id     = transaction_table['dealId']
        offer = OfferIdMap.objects.get(old_id = deal_id).new_offer

        business = offer.business
        redeem      = transaction_table['redeem']
        quantity    = transaction_table['stock']

        transaction_type = TransactionTypes.REDEMPTION
        if redeem != 1:
            transaction_type = TransactionTypes.PURCHASE

        date        = transaction_table['date']
        print "Importing transaction between %s and %s" % (user, business)

        Transaction.objects.create_transaction(
            user,
            business,
            offer,
            transaction_type,
            quantity,
        )

def get_business_from_old_id(old_business_id):

    businesses = BusinessIdMap.objects.filter(old_id = old_business_id)
    if len(businesses) > 0:
        business = businesses[0].new_business

    else:
        business = None


    return business

def get_user_from_old_id(old_user_id, cursor):

    if old_user_id == 0:
        return None

    cursor.execute("""SELECT email FROM users WHERE id = '%s'""" % old_user_id)
    username = cursor.fetchone()
    if username == None:
        print "USER %s NOT IN SYSTEM." % old_user_id
        return None

    username = username['email']
    #sys.stderr.write('username = %s\n' % username)
    user = User.objects.filter(username=username)
    if len(user) > 0:
        return user[0]
    else:
        return None

def import_business_subscriptions(cursor):
    cursor.execute("""select * from followRelationship""")

    all_subscriptions = cursor.fetchall()
    for subscription_table in all_subscriptions:
        user_id         = subscription_table['accountId']
        old_business_id = subscription_table['merchantId']

        business = get_business_from_old_id(old_business_id)
        user = get_user_from_old_id(user_id, cursor)
        print 'Adding business subscription: business = %s, user = %s' % (business, user)

        BusinessSubscription.objects.create(
                user = user,
                business = business,
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
        sys.exit(1)

    c = db.cursor()
    print 'Migration Script!'


    import os
    os.system('./reset.sh')

    import_user(c)
    import_business(c)
    import_cities(c)
    import_neighborhoods(c)
    import_categories(c)
    import_offer(c)

    import_qrcodes(c)
    import_business_links(c)
    import_business_subscriptions(c)
    import_transactions(c)
