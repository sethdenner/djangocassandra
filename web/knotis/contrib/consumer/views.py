from knotis.views import (
    ContextView
)


class MyPurchasesView(ContextView):
    template_name = 'knotis/consumer/my_purchases_view.html'

    def process_context(self):
        return self.context


class MyRelationsView(ContextView):
    template_name = 'knotis/consumer/my_relations_view.html'

    def process_context(self):
        return self.context
