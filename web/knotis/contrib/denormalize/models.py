from fields import *

import sys
TESTING = sys.argv[1:2] == ['test']
if TESTING:
    from tests.models import *
