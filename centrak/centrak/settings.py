"""
Django settings for centrak project.

Generated by 'django-admin startproject' using Django 1.8.13.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
import os
import mongoengine



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hogjdcbnr$27pwn6#o6*b9c$*w@i%1_clyc+%utw-d41%2q0rv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'on') == 'on'
ALLOWED_HOSTS = []
INTERNAL_IPS = [
    '127.0.0.1',
]

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # third-party
    'ezaddress',
    'mongoengine',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_mongoengine',
    
    # internal
    'core',
    'enumeration',
    'main',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'centrak.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # internal
                'main.context_processors.menu',
                'main.context_processors.jsconf',
                'main.context_processors.current_date',
            ],
        },
    },
]

WSGI_APPLICATION = 'centrak.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '..', 'db.sqlite3'),
    }
}

# settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, '..', 'centrak-debug.log')
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, '..', 'centrak-error.log')
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file_debug','file_error'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}


##: ==+: mongo-engine settings
_MONGODB_NAME = 'centrak_'
_MONGODB_HOST = ''
_MONGODB_USER = ''
_MONGODB_PWD  = ''

mongoengine.connect(_MONGODB_NAME)

##: ==+: CELERY
BROKER_URL               = 'redis://localhost:6379'
CELERY_RESULT_BACKEND    = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT    = ['application/json']
CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALISER = 'json'
CELERY_TIMEZONE          = 'Africa/Lagos'


##: ==+: Auth:
LOGIN_URL = '/account/login'
LOGIN_REDIRECT_URL = '/'


##: ==+: Internal
CENTRAK_KEDCO_DOMAINS = ['kedco.ng', 'kedco.net', 'tmp.kedco.ng']
CENTRAK_ADMIN_PREFIX_URL = '/admin/'

CENTRAK_API_ROOT = '/api/v1/'

CENTRAK_TABLE_PAGE_SIZE_LG = 100
CENTRAK_TABLE_PAGE_SIZE = 20


SURVEY_API_SERVICE_KEY = 'survey'
SURVEY_API_ROOT = 'http://survey.kedco.ng/api/v1/data'
SURVEY_AUTH_API_ROOT = 'http://survey.kedco.ng/api/v1/user'
