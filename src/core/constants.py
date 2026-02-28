
from src.__version__ import __version__

APP_TITLE = "Fitba"
APP_AUTHOR = "Caledonius D."
APP_VERSION = [int(x) for x in __version__.split(".")]

def version_str():
    return "v" + ".".join([str(x) for x in APP_VERSION])

