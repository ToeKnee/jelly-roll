__version__ = "0.9.6"

import locale
locale.setlocale(locale.LC_ALL, '')


def get_version():
    "Returns the version as a string."
    return __version__
