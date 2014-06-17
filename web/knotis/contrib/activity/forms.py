###### PYTHON LIBRARY IMPORTS ######
import uuid
import datetime


###### IMPORTS FROM DJANGO ######
from django.utils.log import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.utils.http import urlquote
from django.template import Context
from django.forms import (
    CharField,
    IntegerField,
    ValidationError,
)

###### IMPORTS FROM KNOTIS FILES ######
from knotis.forms import (
    TemplateForm,
)

###### FORM DEFINITIONS ######
class ActivityAdminQueryForm(TemplateForm):
    template_name = 'knotis/activity/activity_admin_form.html'

    range_start = IntegerField(
        label='Start',
        required = True,
        initial = 1,
    )
    range_end = IntegerField(
        label='Stop',
        required = True,
        initial = 20,
    )
    range_step = IntegerField(
        label='Step',
        required = True,
        initial = 20,
    )
    activity_filter = CharField(
        label='Filter',
        max_length = 254,
        required = True,
        initial = '',
    )
