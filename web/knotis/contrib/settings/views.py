










class SettingsGrid(GridSmallView):
    view_name = 'settings_grid'

    def process_context(self):

        current_identity_id = self.request.session.get('current_identity')
        if current_identity_id:
            current_identity = Identity.objects.get(pk=current_identity_id)
        else:
            current_identity = None

        tiles = []

        for setting in settings_views:
            
