import copy
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


class SettingTile(FragmentView):
    template_name = 'knotis/settings/tile.html'
    view_name = 'setting_tile'

class SocialSettingTile(SettingTile):
    template_name = 'knotis/settings/social_tile.html'
	
class QRSettingTile(SettingTile):
    tempalte_name = 'knotis/settings/QR_tile.html'

class SettingsGrid(GridSmallView):
    view_name = 'settings_grid'

    def process_context(self):
        tiles = []
        setting_tiles = [SocialSettingTile, QRSettingTile]
        for setting in setting_tiles:
            setting_context = Context()
            tile = setting()
            tiles.append(
		        tile.render_template_fragment(setting_context)
	        )
			
	local_context = copy.copy(self.context)
	local_context.update({'tiles': tiles})
		
	return local_context

class SettingsView(EmbeddedView):
    url_patterns = [r'^settings/$']
    template_name = 'knotis/settings/settings.html'
    default_parent_view_class = DefaultBaseView

    def process_context(self):
        return self.context
