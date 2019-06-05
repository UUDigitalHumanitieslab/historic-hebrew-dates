""" Settings overrides to quickly enable production mode.

    Magic glue; this is NOT the place for customizations.
"""

import os
import os.path as op

here = op.dirname(op.abspath(__file__))

from settings import *

DEBUG = False

ALLOWED_HOSTS = ['localhost']

STATICFILES_DIRS.pop()  # node_modules not needed in production mode

STATIC_ROOT = op.join(here, 'static')

if not op.exists(STATIC_ROOT):
    os.mkdir(STATIC_ROOT)
