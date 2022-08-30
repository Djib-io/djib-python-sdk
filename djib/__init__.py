__version__ = '0.1.2'

import sys

if sys.version_info < (3, 10):
    raise EnvironmentError("Python 3.10 or above is required.")
