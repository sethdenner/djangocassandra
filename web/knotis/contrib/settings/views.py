import copy
from django.shortcuts import (
    get_object_or_404
)
from django.template import (
    Context
)

from knotis.views import (
    EmbeddedView,
	FragmentView,
)

from knotis.contrib.layout.views import (
    GridSmallView,
	DefaultBaseView,
)

from knotis.contrib.identity.views import (
    Identity,
)


class SocialSettingTile(SettingTile):
    template_name = 'knotis/settings/social_tile.html'
	
class QRSettingTile(SettingTile):
    tempalte_name = 'knotis/settings/QR_tile.html'


class SettingTile(FragmentView):
    template_name = 'knotis/settings/tile.html'
	view_name = 'setting_tile'
	
	def process_context(self):
	    



class SettingsGrid(GridSmallView):
    view_name = 'settings_grid'

    def process_context(self):
        tiles = []

        for setting in settings_views:
            setting_tile = SettingTile
			setting_context = Context()
			tiles.append(
			    setting.render_template_fragment(setting_context)
			)
			
		local_context = copy.copy(self.context)
		local_context.update({'tiles': tiles})
		
		return local_context

class SettingsView(EmbeddedView):
    view_name = 'settings'
	url_patterns = [r'^settings/$']
	template_name = 'knotis/settings/settings.html'
	default_parent_view_class = DefaultBaseView
