import itertools
from collections import OrderedDict
from django.apps import apps

from django.core.management.commands.migrate import (
    Command as DjangoMigrate
)
from django.core.management import call_command
from django.core.management.sql import emit_pre_migrate_signal
from django.core.management.color import no_style


class Command(DjangoMigrate):

    def sync_apps(self, connection, app_labels):
        tables = connection.introspection.table_names()
        seen_models = connection.introspection.installed_models(tables)
        created_models = set()

        all_models = [
            (app_config.label,
                #router.get_migratable_models(app_config, connection.alias, include_auto_created=True))
                app_config.get_models(include_auto_created=True))
            for app_config in apps.get_app_configs()
            if app_config.models_module is not None and app_config.label in app_labels
        ]

        def model_installed(model):
            opts = model._meta
            converter = connection.introspection.table_name_converter

            # Note that if a model is unmanaged we short-circuit and never try
            # to install it
            return not (
                (converter(opts.db_table) in tables) or
                (opts.auto_created and converter(
                    opts.auto_created._meta.db_table
                ) in tables))

        manifest = OrderedDict(
            (app_name, list(filter(model_installed, model_list)))
            for app_name, model_list in all_models
        )
        create_models = set(itertools.chain(*manifest.values()))
        emit_pre_migrate_signal(
            create_models,
            self.verbosity,
            self.interactive,
            connection.alias
        )
        # Create the tables for each model
        if self.verbosity >= 1:
            self.stdout.write("  Creating tables...\n")

        for app_name, model_list in manifest.items():
            for model in model_list:
                # Create the model's database table, if it doesn't already
                # exist.
                if self.verbosity >= 3:
                    self.stdout.write(
                        "    Processing %s.%s model\n" % (
                            app_name, model._meta.object_name))

                if self.verbosity >= 1:
                    self.stdout.write(
                        "    Creating table %s\n" % model._meta.db_table)

                connection.creation.sql_create_model(
                    model,
                    no_style(),
                    seen_models
                )

                seen_models.add(model)
                created_models.add(model)

                tables.append(connection.introspection.table_name_converter(
                    model._meta.db_table
                ))

        if self.load_initial_data:
            for app_label in app_labels:
                call_command(
                    'loaddata',
                    'initial_data',
                    verbosity=self.verbosity,
                    database=connection.alias,
                    skip_validation=True,
                    app_label=app_label,
                    hide_empty=True
                )

        return created_models
