__version__ = "0.10.0.0"

import locale
locale.setlocale(locale.LC_ALL, '')


def get_version():
    "Returns the version as a string."
    return __version__
