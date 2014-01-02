import os
import sys

from django.conf import settings
from django.utils.importlib import import_module
from django.template.loaders.app_directories import Loader as AppLoader


fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
knotis_app_path = 'knotis/contrib/'
app_template_dirs = []
for app in os.listdir(
    os.path.join(
        settings.PROJECT_ROOT,
        knotis_app_path
    )
):
    try:
        mod = import_module('.'.join([
                'knotis',
                'contrib',
                app
            ])
        )

    except ImportError, e:
        continue

    template_dir = os.path.join(os.path.dirname(mod.__file__), 'templates')
    if os.path.isdir(template_dir):
        app_template_dirs.append(template_dir.decode(fs_encoding))


class Loader(AppLoader):
    def get_template_sources(
        self,
        template_name,
        template_dirs=None
    ):
        return super(Loader, self).get_template_sources(
            template_name,
            app_template_dirs
        )


_loader = Loader()


def load_template_source(
    template_name,
    template_dirs=None
):
    import warnings
    warnings.warn((
            "'django.template.loaders.app_directories.load_template_source' "
            "is deprecated; use 'django.template.loaders.app_directories.Loa"
            "der' instead."
        ),
        DeprecationWarning
    )
    return _loader.load_template_source(
        template_name,
        template_dirs
    )
load_template_source.is_usable = True
