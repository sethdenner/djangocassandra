from app.models.offers import Offer, OfferStatus

offers = Offer.objects.all()

count = 0

num_offers = len(offers)

while (count < 60 and count < num_offers):
    if offers[count].status != OfferStatus.CURRENT or not offers[count].active or not offers[count].published:
        offers[count].status = OfferStatus.CURRENT
        offers[count].active = True
        offers[count].published = True
        offers[count].category.active_offer_count = offers[count].category.active_offer_count + 1
        if count % 5:
            offers[count].premium = True
        offers[count].save()
        count = count + 1
        print 'Upgraded %s' % (offers[count].title_short(),)
    count = count + 1
