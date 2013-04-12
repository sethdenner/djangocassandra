import sys
import imp
import inspect

from django.conf import settings
from django.template.loader import get_template


class RenderTemplateFragmentMixin(object):
    registered_fragments = {}
    template_name = None
    view_name = None

    @classmethod
    def register_template_fragment(cls):
        RenderTemplateFragmentMixin.registered_fragments[
            cls.view_name
        ] = cls

    @classmethod
    def render_template_fragment(
        cls,
        context
    ):
        template = get_template(cls.template_name)
        return template.render(context)

    @staticmethod
    def register_template_fragment_views(apps=None):
        """
        Register classes in views modules of installed apps
        that implement RenderTemplateFragmentMixin.

        Param: apps - iterable of strings representing module names.
        """
        if not apps:
            apps = settings.INSTALLED_APPS

        for app in apps:
            view_module_name = '.'.join([
                app,
                'views'
            ])
            if view_module_name in sys.modules:
                view_module = sys.modules[view_module_name]

            else:
                try:
                    file, filepath, description = None, None, None
                    for name in view_module_name.split('.'):
                        file, filepath, description = imp.find_module(
                            name,
                            [filepath] if filepath else sys.path
                        )

                        if file:
                            break

                except ImportError:
                    continue

                try:
                    view_module = imp.load_module(
                        view_module_name,
                        file,
                        filepath,
                        description
                    )

                except ImportError:
                    continue

            if not view_module:
                continue

            class_members = inspect.getmembers(
                view_module,
                inspect.isclass
            )

            for c in class_members:
                name, cls = c
                if issubclass(
                    cls,
                    RenderTemplateFragmentMixin
                ) and (
                    cls.__name__ != RenderTemplateFragmentMixin.__name__
                ):
                    print 'registering template fragment %s' % name,
                    cls.register_template_fragment()
