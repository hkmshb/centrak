import mongoengine
from .settings_base import *



DEBUG = False
SECRET_KEY = '?'
ALLOWED_HOSTS = ['?']
INTERNAL_IPS = ['localhost', '127.0.0.1']


## database connections
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        _DBNAME_: '?',
        _DBUSR_: '?',
        _DBPWD_: '?',
    }
}


##: ==+: mongo-engine settings
_MONGODB_NAME = '?'
_MONGODB_USR = '?'
_MONGODB_PWD = '?'
mongoengine.connect(host='mongodb://{}:{}@localhost/{}'.format(
    _MONGODB_USR, _MONGODB_PWD, _MONGODB_NAME))

