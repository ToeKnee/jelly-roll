__version__ = "0.6.4"

import locale
locale.setlocale(locale.LC_ALL, '')


def get_version():
    "Returns the version as a string."
    return __version__
