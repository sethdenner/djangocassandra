#from app.models.contentvs import Content
import getpass
import MySQLdb.cursors

from django.contrib.auth import authenticate

from optparse import OptionParser
from knotis_auth.models import User, AccountTypes, AccountStatus
from knotis_auth.views import _generate_facebook_password
from app.models.businesses import Business, BusinessLink, BusinessSubscription
from app.models.offers import Offer
from app.models.cities import City
from knotis_qrcodes.models import Qrcode, QrcodeTypes, Scan
from app.models.categories import Category
from app.models.transactions import Transaction, TransactionTypes
from app.models.endpoints import Endpoint, EndpointTypes
from app.models.media import Image

import datetime
import sys

from app.models.neighborhoods import Neighborhood

from legacy.models import UserIdMap, BusinessIdMap, OfferIdMap, QrcodeIdMap

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

    for user_table in all_users:
        try:
            email = user_table['email'].decode('cp1252')

            first_name = user_table['firstName'].decode('cp1252')
            last_name = user_table['lastName'].decode('cp1252')

            status = user_table['status'] # enum('banned','inactive','validating','active')
            password = user_table['password']
            salt = user_table['salt']

            # user-> account_type != 1 == subscription = yes.
            # role -> role_id = 2 = business
            # role -> role_id (3,4) = admin
            # except ... it's busted so all merchants are on the paid account...

            # default is USER
            account_type = AccountTypes.USER
            role = user_table['role_id']
            if role == 2:
                account_type = AccountTypes.BUSINESS_MONTHLY

            current_users = User.objects.filter(username=email)
            if current_users.count() > 0:
                print 'User %s is already in the database.' % email
                continue

            print 'Importing user %s with type %s' % (email, account_type)

            user, user_profile = User.objects.create_user(
                first_name,
                last_name,
                email,
                'whatever nuke in next statement',
                account_type=account_type
            )

            facebook_id = user_table['facebook_id']
            if password:
                user.password = '$'.join([
                    'sha1',
                    salt,
                    password
                ])

            elif facebook_id:
                user.password = _generate_facebook_password(facebook_id)

            else:
                raise Exception(
                    'could not convert password for user %s' % email,
                )

            old_user_id = user_table['id']
            UserIdMap.objects.create(
                old_id=old_user_id,
                new_user=user
            )

            if status.lower() == 'active':
                user_profile.account_status = AccountStatus.ACTIVE
                user.active = True

            else:
                user_profile.account_status = AccountStatus.DISABLED

            user_profile.save()
            user.save()

            Endpoint.objects.create_endpoint(
                EndpointTypes.EMAIL,
                email,
                user,
                True
            )

        except Exception as e:
            print 'Exception!: %s\n' % e,

#     import business
def import_business(cursor):

    cursor.execute('''SELECT * FROM merchantProfile, users
                      WHERE users.id = merchantProfile.userId''')

    all_businesses = cursor.fetchall()
    for business_table in all_businesses:
        try:
            name = business_table['name'].decode('cp1252')
            phone = business_table['phone'].decode('cp1252')

            summary = business_table['description'].decode('cp1252')
            description = business_table['extendedDescription'].decode('cp1252')

            address = business_table['street1'].decode('cp1252') #+ business_table['street2'].decode('cp1252')

            twitter_name = business_table['twitter'].decode('cp1252')
            facebook_uri = business_table['facebook'].decode('cp1252')
            yelp_id = business_table['yelp'].decode('cp1252')

            # Getting the user id for the new system.
            old_user_id = business_table['userId']
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
                yelp_id
            )

            old_id = business_table['id']
            BusinessIdMap.objects.create(
                old_id=old_id,
                new_business=new_business
            )

            qrcode_legacy_type = business_table['qrcodeType']
            qrcode_uri = business_table['qrcodeContent']
            if 'deal' == qrcode_legacy_type:
                qrcode_type = QrcodeTypes.OFFER

            elif 'video' == qrcode_legacy_type:
                qrcode_type = QrcodeTypes.VIDEO

            elif 'link' == qrcode_legacy_type:
                qrcode_type = QrcodeTypes.LINK

            else:
                qrcode_type = QrcodeTypes.PROFILE

            qrcode = Qrcode.objects.create(
                business=new_business,
                uri=qrcode_uri,
                qrcode_type=qrcode_type
            )

            QrcodeIdMap.objects.create(
                old_id=business_table['qrcodeId'],
                new_qrcode=qrcode
            )

        except Exception as e:
            print 'Exception!: %s\n' % e,

#     import deal
def import_offer(cursor):
    cursor.execute("""SELECT * from deal, users where users.id = deal.usersId""")
    all_offers = cursor.fetchall()
    for old_offer in all_offers:
        try:
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
            businesses = BusinessIdMap.objects.filter(old_id=old_business_id)
            if len(businesses) > 0:
                #print businesses
                business = businesses[0].new_business

            title = old_offer['title'].decode('cp1252')
            title_type = old_offer['titleType']
            description = old_offer['description'].decode('cp1252')
            restrictions = old_offer['extendedDescription'].decode('cp1252')


            # Get city instance.
            city_id = old_offer['cityId']
            cursor.execute("""select title from city where id=%s""" % city_id)
            city_name = cursor.fetchone()
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
            address = old_offer['address'].decode('cp1252')

            # Get neighborhood instance.
            neighborhood_id = old_offer['neightbourhoodId']
            cursor.execute("""select title from neighbourhood where id = %s""" % neighborhood_id)

            neighborhood_name = cursor.fetchone()
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

            image = '/'.join([
                'images',
                old_offer['image']
            ])

            # Get the category instance.
            category_id = old_offer['categoryId']
            cursor.execute("""select title from category where id = %s""" % category_id)
            category_name = cursor.fetchone()
            category = None
            if category_name == None:
                print "Category of id %s not in database." % category_id

            else:
                category_name = category_name['title'].decode('cp1252')
                for curr_category in Category.objects.all():
                    if curr_category.name.value == category_name:
                        category = curr_category
                        break

            price_retail = old_offer['oldprice']
            price_discount = old_offer['newprice']
            start_date = old_offer['startDate']
            end_date = old_offer['endDate']
            stock = old_offer['stock']
            unlimited = old_offer['unlimited']
            published = old_offer['Published']
            premium = old_offer['premium']
            active = old_offer['active']
            end_date = old_offer['endDate']

            if premium == 1:
                premium = True

            else:
                premium = False

            if end_date < datetime.datetime.now() or not published:
                active = False

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
                published,
                premium
            )
            new_offer.active = active
            new_offer.save()

            old_offer_id = old_offer['id']

            OfferIdMap.objects.create(
                old_id=old_offer_id,
                new_offer=new_offer
            )

        except Exception as e:
            print 'Exception!: %s\n' % e,


def import_categories(
    cursor,
    user
):
    cursor.execute("""select * from category""")
    all_categories = cursor.fetchall()
    for category_dict in all_categories:
        try:
            name = category_dict['title'].decode('cp1252')
            print 'Importing category %s by %s' % (name, user)
            Category.objects.create_category(user, name)

        except Exception as e:
            print 'Exception!: %s\n' % e,


def import_cities(
    cursor,
    user
):
    cursor.execute("""select * from city;""")
    all_cities = cursor.fetchall()
    for city_dict in all_cities:
        try:
            city_name = city_dict['title'].decode('cp1252')

            new_city = City.objects.create_city(user=user, name=city_name)

            print 'City %s added by %s' % (new_city.name, user)

        except Exception as e:
            print 'Exception!: %s\n' % e,


def import_neighborhoods(
    cursor,
    user
):
    cursor.execute("""select * from neighbourhood""")
    all_neighborhoods = cursor.fetchall()
    for neighborhood_dict in all_neighborhoods:
        try:
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
            print "%s creating neighborhood %s in %s" % (user, name, city_name)
            Neighborhood.objects.create_neighborhood(
                user,
                city,
                name
            )

        except Exception as e:
            print 'Exception!: %s\n' % e,


#     import qrcodes
def import_scans(cursor):

    cursor.execute("""select * from qrcodeHistory""")
    all_scans = cursor.fetchall()
    for scan in all_scans:
        try:
            old_business_id = scan['merchantId']
            uri = scan['link'].decode('cp1252')

            business_map = BusinessIdMap.objects.get(old_id=old_business_id)
            qrcode = Qrcode.objects.get(business=business_map.new_business)
            scan_type = scan['qrcodeType']
            scan_date = scan['date']

            print 'Importing qrcode scan: old_business_id = %s, qrcode_type = %s, uri = %s, qrcode_date = %s' \
                % (old_business_id, scan_type, uri, scan_date)

            scan = Scan.objects.create(
                qrcode=qrcode,
                business=qrcode.business,
                uri=uri,
            )

            scan.pub_date = scan_date
            scan.save()

            qrcode.hits = qrcode.hits + 1
            if qrcode.last_hit < scan_date:
                qrcode.last_hit = scan_date

            qrcode.save()

        except Exception as e:
            print 'Exception!: %s\n' % e,


def import_business_links(cursor):
    cursor.execute('''select * from merchantLinks''')
    all_links = cursor.fetchall()
    for link_table in all_links:
        try:
            old_business_id = link_table['merchantId']
            uri = link_table['urlLink'].decode('cp1252')
            title = link_table['titleLink'].decode('cp1252')

            businesses = BusinessIdMap.objects.filter(old_id=old_business_id)
            business = None
            if len(businesses) > 0:
                business = businesses[0].new_business
            print 'Importing business link for %s to %s' % (business, uri)
            new_business_link = BusinessLink(
                business=business,
                uri=uri,
                title=title,
            )
            new_business_link.save()

        except Exception as e:
            print 'Exception!: %s\n' % e,


def import_images(cursor):
    cursor.execute('''select * from asset''')
    all_assets = cursor.fetchall()
    for asset in all_assets:
        asset_type = asset['type'].decode('cp1252')
        old_related_id = asset['idRel']
        try:
            if 'deal' == asset_type:
                offer_map = OfferIdMap.objects.filter(old_id=old_related_id)[0]
                related_object_id = offer_map.new_offer_id
                user = offer_map.new_offer.business.user

            elif 'business' == asset_type:
                business_map = BusinessIdMap.objects.filter(old_id=old_related_id)[0]
                related_object_id = business_map.new_business_id
                user = business_map.new_business.user

            else:
                related_object_id = None
                user = None

            image = '/'.join([
                'images',
                asset['location']
            ])

            print 'Importing image "%s" by user "%s" for object with id "%s".' % (
                image,
                user.username,
                related_object_id
            )

            image_instance = Image.objects.create_image(
                user,
                image,
                None,
                related_object_id
            )

            if 'business' == asset_type:
                if asset['headImage']:
                    business_map.new_business.primary_image = image_instance
                    business_map.new_business.save()

        except Exception, e:
            print 'Exception!: %s\n' % e,


def import_transactions(cursor):
    cursor.execute('''select * from dealOrder,users where users.id = dealOrder.accountId''')
    all_transactions = cursor.fetchall()
    for transaction_table in all_transactions:
        try:
            username = transaction_table['email'].decode('cp1252')
            user = User.objects.get(username=username)

            deal_id = transaction_table['dealId']
            offer = OfferIdMap.objects.get(old_id=deal_id).new_offer
            business = offer.business
            redeem = transaction_table['redeem']
            quantity = transaction_table['stock']
            price = transaction_table['price']
            transaction_context = transaction_table['txn_id']

            transaction_type = TransactionTypes.REDEMPTION
            if redeem != 1:
                transaction_type = TransactionTypes.PURCHASE

            date = transaction_table['date']
            print "Importing transaction between %s and %s" % (user, business)

            transaction = Transaction.objects.create_transaction(
                user,
                transaction_type,
                business,
                offer,
                quantity,
                price,
                transaction_context
            )
            transaction.pub_date = date
            transaction.save()

        except Exception as e:
            print 'Exception!: %s\n' % e,


def get_business_from_old_id(old_business_id):
    business_map = BusinessIdMap.objects.get(old_id=old_business_id)
    return business_map.new_business


def get_user_from_old_id(old_user_id):
    user_map = UserIdMap.objects.get(old_id=old_user_id)
    return user_map.new_user


def import_business_subscriptions(cursor):
    cursor.execute("""select * from followRelationship""")

    all_subscriptions = cursor.fetchall()
    for subscription_table in all_subscriptions:
        try:
            old_user_id = subscription_table['accountId']
            old_business_id = subscription_table['merchantId']

            business = get_business_from_old_id(old_business_id)
            user = get_user_from_old_id(old_user_id)
            print 'Adding business subscription: business = %s, user = %s' % (business, user)

            BusinessSubscription.objects.create(
                user=user,
                business=business,
                active=True
            )

        except Exception as e:
            print 'Exception!: %s\n' % e,


if __name__ == '__main__':


    parser = OptionParser()
    parser.add_option(
        '-u',
        '--superuser',
        dest='superuser',
        help='Super user to use for creating default content',
        metavar='SUPERUSER'
    )

    (options, args) = parser.parse_args()

    if options.superuser is None:
        print "A mandatory option is missing\n"
        parser.print_help()
        sys.exit(-1)


    password = getpass.getpass('Enter password: ')
    try:
        superuser = authenticate(
            username=options.superuser,
            password=password
        )
    except:
        superuser = None

    if not superuser or not superuser.is_staff or not superuser.is_superuser:
        print "This user is not a super user. Run python manage.py createsuperuser\n"
        parser.print_help()
        sys.exit(-1)

    #host = options['host']
    host = '216.70.69.66'

    #user = options['user']
    user = 'cHAsTE2r'

    #sqlDB = options['db']
    sqlDB = 'mclean_knotis'

    #password = getpass.getpass('Enter password:')
    password = 'pHUb9ge4'

    try:
        db = MySQLdb.connect(
            host=host,
            user=user,
            passwd=password,
            db=sqlDB,
            cursorclass=MySQLdb.cursors.DictCursor,
        )

    except:
        print 'Database connect error!'
        sys.exit(1)

    c = db.cursor()
    print 'Migration Script!'

    #import os
    #os.system('./reset.sh')

    import_user(c)
    import_business(c)
    import_business_links(c)

    import_cities(
        c,
        superuser
    )
    import_neighborhoods(
        c,
        superuser
    )
    import_categories(
        c,
        superuser
    )
    import_offer(c)

    import_transactions(c)
    import_images(c)
    import_scans(c)

    import_business_subscriptions(c)
