from knotis.views import EmailView


class NewOfferEmailView(EmailView):
    template_name = 'knotis/offer/email_new_offer.html'
    text_template_name = 'knotis/offer/email_new_offer.txt'
