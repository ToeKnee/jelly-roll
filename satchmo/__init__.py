__version__ = "0.9.7.8"

import locale
locale.setlocale(locale.LC_ALL, '')


def get_version():
    "Returns the version as a string."
    return __version__
