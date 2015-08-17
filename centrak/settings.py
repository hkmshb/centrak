"""
Django settings for centrak project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
import os
from django.core.exceptions import ImproperlyConfigured



def get_env_var(name, default=None):
    """Gets """
    try:
        if default:
            return os.environ.get(name, default)
        return os.environ[name]
    except KeyError:
        error_msg = "Set the %s environment variable" % name
        raise ImproperlyConfigured(error_msg)
    
    

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@yd=&3nra63*70ft-rnub!z$+uzr3hsvk4%k0oqo4cqt+acntm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env_var('CENTRAK_DEBUG', True)
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # centrak apps
    'enumeration',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'centrak.urls'
WSGI_APPLICATION = 'centrak.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'NAME': 'CenTrak',
        'ENGINE': 'sqlserver_ado',
        'HOST': get_env_var('CENTRAK_DB_HOST'),
        'USER': '',
        'PASSWORD': '',
        'OPTIONS': {
            'provider': 'SQLOLEDB',
            'use_mars': False,
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
