from knotis.views import (
    ContextView
)


class MyEstablishmentsView(ContextView):
    template_name = 'knotis/merchant/my_establishments_view.html'

    def process_context(self):
        return self.context


class MyOffersView(ContextView):
    template_name = 'knotis/merchant/my_offers_view.html'

    def process_context(self):
        return self.context


class OfferRedemptionView(ContextView):
    template_name = 'knotis/merchant/offer_redemption_view.html'

    def process_context(self):
        return self.context


class MyFollowersView(ContextView):
    template_name = 'knotis/merchant/my_followers_view.html'

    def process_context(self):
        return self.context


class MyAnalyticsView(ContextView):
    template_name = 'knotis/merchant/my_analytics_view.html'

    def process_context(self):
        return self.context
