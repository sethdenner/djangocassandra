import json
import itertools
import traceback
import datetime
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('INFO'))

from collections import OrderedDict
from optparse import make_option
from pprint import PrettyPrinter
from django.apps import apps
from django.conf import settings

from django.core.management.base import (
    BaseCommand,
    CommandError
)

from django.db.models import (
    ForeignKey,
    BooleanField
)

from django.contrib.contenttypes.models import ContentType

from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily

from cassandra.query import ordered_dict_factory
from cassandra.cqlengine.connection import (
    setup as cql_setup,
    get_session as cql_get_session
)

from knotis.utils.signals import DisableSignals


class CassandraBackendTypes:
    CQL3 = 'cql3'
    THRIFT = 'thrift'

class Command(BaseCommand):
    args = (
        '<contact-point0> <contact-pointaddress1> ... '
        '-p | --port <listenPort> '
        '-m | --models <appName> <appName.Model> <appName.Model> ... '
        '-x | --exclude <appName> <appName.Model> <appName.Model> ... '
        '-u | --auth-type <authType> '
        '-a | --auth-credentials <credentials> '
    )
    option_list = BaseCommand.option_list + (
        make_option(
            '--contacts', '-c',
            action='append',
            dest='contacts',
            default=[],
            help=(
                'Add a contact point for your Cassandra cluster.'
            )
        ),
        make_option(
            '--port', '-p',
            action='store',
            dest='port',
            default=9042,
            type='int',
            help=(
                'Set the port that listens for cql clients in your cluster.'
            )
        ),
        make_option(
            '--model', '-m',
            action='append',
            dest='models',
            default=[],
            help=(
                'Add a specific model or app to the import.'
            )
        ),
        make_option(
            '--exclude', '-x',
            action='append',
            dest='exclude',
            default=[],
            help=(
                'Exclude a model or app from the import.'
            )
        ),
        make_option(
            '--keyspace', '-k',
            action='store',
            dest='keyspace',
            default=None,
            help=(
                'Set the default keyspace to use. Otherwise this '
                'is gathered from settings.py.'
            )
        ),
        make_option(
            '--backend', '-b',
            action='store',
            dest='backend',
            default=CassandraBackendTypes.CQL3,
            help=(
                'Choose wether to use the new CQL3 (cql3) backend or the '
                'legacy Thrift (thrift) interface. Note: Cassandra listens '
                'thrift clients on port 9160 by default instead of 9042.'
            )
        ),
        make_option(
            '--limit', '--max', '-l',
            action='store',
            dest='limit',
            default=None,
            type='int',
            help=(
                'Limit the total number of rows imported. Import will exit '
                'once this number of total rows has been sucessfully imported.'
            )
        )
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(Command, self).__init__(
            *args,
            **kwargs
        )

        self.row_errors = []
        self.export_errors = []
        self.total_models_imported = 0
        self.total_rows_imported = 0
        self.total_export_errors = 0
        self.total_row_errors = 0
        self.start_time = datetime.datetime.now()

    def get_import_models(
            self,
            **options
    ):
        all_apps = [
            label.split('.')[-1]
            for label
            in settings.INSTALLED_APPS
            if label != 'contenttypes'
        ]
        '''
        Don't include content types as they are
        automatically generated if they don't exist.
        '''

        all_models = [(
                app_config.label,
                app_config.get_models(
                    include_auto_created=True
                )
            )
            for app_config in apps.get_app_configs()
            if app_config.models_module is not None
            and app_config.label in all_apps
        ]

        include_options = options['models']
        include_apps = []
        include_models = {}
        for option in include_options:
            split_option = option.split('.')
            split_len = len(split_option)
            if 1 == split_len:
                include_apps.append(option)

            elif 2 == split_len:
                app = split_option[0]
                model = split_option[1]
                models = include_models.get(app, [])
                models.append(model)
                include_models[app] = models

            else:
                raise Exception('Bad parameter')
                    
        exclude_options = options['exclude']
        exclude_apps = []
        exclude_models = {}
        for option in exclude_options:
            split_option = option.split('.')
            split_len = len(split_option)
            if 1 == split_len:
                exclude_apps.append(option)

            elif 2 == split_len:
                app = split_option[0]
                model = split_option[1]
                models = exclude_models.get(app, [])
                models.append(model)
                exclude_models[app] = models

            else:
                raise Exception('Bad parameter')

        filtered_models = []
        for app, models in all_models:
            if app in exclude_apps:
                continue

            if (
                include_apps
                and app not in include_apps
                and not include_models
            ):
                continue

            for model in models:
                if app in exclude_models:
                    if model.__name__ in exclude_models[app]:
                        continue

                if not include_models:
                    filtered_models.append(model)

                elif (
                    app in include_models
                    and model.__name__ in include_models[app]
                ):
                    filtered_models.append(model)

                else:
                    continue

        import_models = []
        for model in filtered_models:
            if (
                model._meta.abstract
                or model._meta.proxy
            ):
                continue

            import_models.append(model)

        return import_models

    def normalize_field_name(
        self,
        field
    ):
        field_name = (
            field.db_column
            if field.db_column
            else field.name
        )

        if isinstance(field, ForeignKey):
            field_name = '_'.join([
                field_name,
                'id'
            ])

        return field_name

    def _obtain_thrift_connection(
        self,
        contact_points,
        default_keyspace,
        port
    ):
        contact_points = [':'.join([
            contact,
            str(port)
        ]) for contact in contact_points]
        connection = ConnectionPool(
            default_keyspace,
            contact_points
        )

        self.backend_type = CassandraBackendTypes.THRIFT
        self.connection = connection
        return self.connection

    def _obtain_cql3_connection(
            self,
            contact_points,
            default_keyspace,
            port
    ):
        connection = cql_setup(
            contact_points,
            default_keyspace,
            port=port
        )

        session = cql_get_session()
        session.row_factory = ordered_dict_factory
        session.set_keyspace(default_keyspace)

        self.backend_type = CassandraBackendTypes.CQL3
        self.connection = session
        return self.connection

    def obtain_connection(
        self,
        **options
    ):
        contact_points = options['contacts']
        default_keyspace = options['keyspace']
        port = options['port']

        backend_type = options['backend'].lower()
        if CassandraBackendTypes.CQL3 == backend_type:
            return self._obtain_cql3_connection(
                contact_points,
                default_keyspace,
                port
            )

        elif CassandraBackendTypes.THRIFT == backend_type:
            return self._obtain_thrift_connection(
                contact_points,
                default_keyspace,
                port
            )

        else:
            raise Exception(
                'Backend Type "%s" not supported'
                % (backend_type,)
            )

    def _get_rows_for_model_thrift(
        self,
        model
    ):
        column_family = ColumnFamily(
            self.connection,
            model._meta.db_table
        )

        results = column_family.get_range()

        fields = {
            self.normalize_field_name(
                field
            ): field
            for field
            in model._meta.fields
        }
        pk_field = model._meta.pk

        rows = []
        for result in results:
            row = {
                pk_field.db_column
                if pk_field.db_column
                else pk_field.name: result[0]
            }

            for key, value in result[1].iteritems():
                field = fields[key]
                if isinstance(field, ForeignKey):
                    related_model = field.rel.to
                    if issubclass(related_model, ContentType):
                        if key.endswith('_id'):
                            key = key[:-3]

                        content_type_column_family = ColumnFamily(
                            self.connection,
                            ContentType._meta.db_table
                        )
                        contenttype_instance = content_type_column_family.get(
                            value
                        )

                        value = ContentType.objects.get_by_natural_key(
                            contenttype_instance['app_label'],
                            contenttype_instance['model']
                        )

                elif isinstance(field, BooleanField):
                    if value.lower() in [
                        'false',
                        'f',
                        'no',
                        'n',
                    ]:
                        value = False

                    else:
                        value = True

                try:
                    value = (
                        value.decode('utf-8')
                        if isinstance(value, basestring)
                        else value
                    )
                    if value == '\x08' or value == '\b':
                        value = None

                except:
                    pass

                row[key] = value

            rows.append(row)

        return rows

    def _get_rows_for_model_cql3(
        self,
        model
    ):
        db_table = model._meta.db_table
        query = ' '.join([
            'select',
            '*',  #', '.join(field_names),
            'from',
            db_table
        ])

        print 'Executing CQL3 query:\n\n\t%s\n\n' % query,

        return self.connection.execute(
            query
        )

    def get_rows_for_model(
        self,
        model
    ):
        if CassandraBackendTypes.CQL3 == self.backend_type:
            return self._get_rows_for_model_cql3(model)

        elif CassandraBackendTypes.THRIFT == self.backend_type:
            return self._get_rows_for_model_thrift(model)

    def handle(
        self,
        *args,
        **options
    ):
        verbosity = int(options['verbosity'])
        cassandra_log = logging.getLogger('cassandra')
        if verbosity >= 4:
            cassandra_log.setLevel(logging.getLevelName('INFO'))

        elif verbosity >= 3:
            cassandra_log.setLevel(logging.getLevelName('DEBUG'))

        else:
            cassandra_log.setLevel(logging.getLevelName('ERROR'))

        import_models = self.get_import_models(**options)
        connection = self.obtain_connection(**options)

        maximum_rows = options['limit']
        for model in import_models:
            if (
                None is not maximum_rows
                and maximum_rows <= self.total_rows_imported
            ):
                break

            db_table = model._meta.db_table
            logger.info(''.join([
                'Exporting Rows for ',
                model.__name__,
                ' (',
                db_table,
                ')...'
            ]))
            try:
                rows = self.get_rows_for_model(model)
                logger.info(''.join([
                    'Exporting Rows for ',
                    model.__name__,
                    ' (',
                    db_table,
                    ') Completed.'
                ]))

            except Exception, e:
                logger.error(''.join([
                    'Exporting Rows for ',
                    model.__name__,
                    ' (',
                    db_table,
                    ') FAILED!'
                ]))
                self.export_errors.append((
                    model,
                    e,
                    traceback.format_exc().encode('string_escape')
                ))
                self.total_export_errors += 1
                continue

            if rows:
                logger.info(''.join([
                    'Importing Rows for ',
                    model.__name__,
                    ' (',
                    db_table,
                    ')...'
                ]))
                current_row_errors = self.total_row_errors
                for row in rows:
                    try:
                        new_instance = model(**row)
                        with DisableSignals():
                            new_instance.save()

                        self.total_rows_imported += 1

                        if (
                            None is not maximum_rows
                            and maximum_rows <= self.total_rows_imported
                        ):
                            break

                    except Exception, e:
                        self.total_row_errors += 1
                        self.row_errors.append((
                            model,
                            row,
                            e,
                            traceback.format_exc()
                        ))

                        
                new_errors = self.total_row_errors - current_row_errors
                logger.info(''.join([
                    'Importing Rows for ',
                    model.__name__,
                    ' (',
                    db_table,
                    ') Completed',
                    ' '.join([
                        ' With',
                        str(new_errors),
                        'ERRORS!'
                    ]) if new_errors > 0 else '.'
                ]))
                self.total_models_imported += 1

        end_time = datetime.datetime.now()

        if self.export_errors:
            with open('export-errors.log', 'w') as f:
                pp = PrettyPrinter(
                    indent=4,
                    width=-1,
                    stream=f
                )
                for e in self.export_errors:
                    pp.pprint(e)

        if self.row_errors:
            with open('import-errors.log', 'w') as f:
                pp = PrettyPrinter(
                    indent=4,
                    width=-1,
                    stream=f
                )
                for e in self.row_errors:
                    pp.pprint(e)

        logger.info('\nTotal Models Imported: %s\n' % self.total_models_imported,)
        logger.info('Total Rows Imported: %s\n' % self.total_rows_imported,)
        logger.info('Total Export Errors: %s\n' % self.total_export_errors,)
        logger.info('Total Import Errors: %s\n' % self.total_row_errors,)
        logger.info('Start Time: %s\n' % self.start_time,)
        logger.info('End Time: %s\n' % end_time,)
        logger.info('Completed in %s seconds.\n' % ((end_time - self.start_time).seconds,))
