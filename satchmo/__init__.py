VERSION = (0, 5, 0)
import logging
import locale
import os

def get_version():
    "Returns the version as a human-format string."
    v = '.'.join([str(i) for i in VERSION[:-1]])
    if VERSION[-1]:
        import satchmo
        from django.utils.version import get_svn_revision
        v = '%s-%s-%s' % (v, VERSION[-1], get_svn_revision(path=satchmo.__path__[0]))
    return v

locale.setlocale(locale.LC_ALL, '')

#Configure logging
LOGFILE = os.path.join("/", "var", "log", "jelly-roll.log")
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=LOGFILE,
                    filemode='a+')

# define a Handler which writes INFO messages or higher to the sys.stderr
fileLog = logging.FileHandler(LOGFILE, 'a+')
fileLog.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
fileLog.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(fileLog)
logging.getLogger('caching').setLevel(logging.INFO)
logging.info("Jelly Roll started")

