import sys
import imp
import inspect

from django.utils import log
logger = log.getLogger(__name__)

from django.conf import settings
from django.core.management.base import (
    BaseCommand,
    CommandError
)

from django.db.models import Model


class Command(BaseCommand):
    def handle(
        self,
        *args,
        **options
    ):
        models = []
        apps = []

        if not apps:
            apps = settings.INSTALLED_APPS

        for app in apps:
            model_module_name = '.'.join([
                app,
                'models'
            ])
            if model_module_name in sys.modules:
                model_module = sys.modules[model_module_name]

            else:
                try:
                    file, filepath, description = None, None, None
                    for name in model_module_name.split('.'):
                        file, filepath, description = imp.find_module(
                            name,
                            [filepath] if filepath else sys.path
                        )

                        if file:
                            break

                except ImportError:
                    continue

                try:
                    model_module = imp.load_module(
                        model_module_name,
                        file,
                        filepath,
                        description
                    )

                except ImportError:
                    continue

            if not model_module:
                continue

            class_members = inspect.getmembers(
                model_module,
                inspect.isclass
            )

            for c in class_members:
                name, cls = c
                if hasattr(
                    cls,
                    'Meta'
                ):
                    meta = cls.Meta

                else:
                    meta = None

                if issubclass(
                    cls,
                    Model
                ) and (not meta or ((
                    not hasattr(
                        meta,
                        'proxy'
                    ) or not meta.proxy
                ) and (
                    not hasattr(
                        meta,
                        'abstract'
                    ) or not meta.abstract
                ))):
                    models.append(cls)

        for model in models:
            print model
