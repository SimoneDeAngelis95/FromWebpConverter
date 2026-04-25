import platform
import os

APP_NAME = "From Webp Converter"
APP_VERSION = "1.0.2"


if platform.system() in ('Darwin', 'Linux'):
    DEFAULT_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')
elif platform.system() == 'Windows':
    DEFAULT_PATH = os.path.join(os.environ.get('USERPROFILE', os.path.expanduser('~')), 'Desktop')
else:
    DEFAULT_PATH = os.path.expanduser('~') # if os is not recognized, return home (~)