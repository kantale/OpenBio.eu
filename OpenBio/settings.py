"""
Django settings for OpenBio project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!!!!!!!!!!!!!!!thisisnotasecretkey!!!!!!!!!!!!!!!!'

# if 'thisisnotasecretkey' in SECRET_KEY:
#     print ('WARNING: SECRET KEY IS NOT SET!!')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'social_django',  #  DO NOT FORGET TO: SOCIAL_AUTH_POSTGRES_JSONFIELD = True
                      # https://python-social-auth.readthedocs.io/en/latest/configuration/django.html
    'rest_framework',
    'rest_framework.authtoken',

    'app',
]


AUTHENTICATION_BACKENDS = (
    #'social_core.backends.orcid.ORCIDOAuth2Sandbox',
    'social_core.backends.orcid.ORCIDOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'OpenBio.urls'

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

                # python-social-auth
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

LOGIN_REDIRECT_URL = '/platform/'
# https://python-social-auth.readthedocs.io/en/latest/configuration/settings.html
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/platform/?orcid=success'
# SOCIAL_AUTH_LOGIN_ERROR_URL = ...  # TODO

SOCIAL_AUTH_ORCID_KEY='APP-XXXYYYZZZ'
SOCIAL_AUTH_ORCID_SECRET='XXXYYYZZZ'

# If set, do not show "sign up" button, but "log in" with specific backend
LOGIN_BACKEND = ''

WSGI_APPLICATION = 'OpenBio.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_CONTENT_NEGOTIATION_CLASS': 'app.negotiation.IgnoreClientContentNegotiation',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}


# Interface customization

TITLE = 'OpenBio.eu'
SERVER = 'https://www.openbio.eu'
EMAIL = 'info@www.openbio.eu'
ADMIN = 'kantale@ics.forth.gr' # In case the email fail, use this instead
TERMS = 'https://www.openbio.eu/static/static/static/docs/terms_privacy/OpenBio_Conditions.pdf' # URL OF TERMS OF USE
PRIVACY = 'https://www.openbio.eu/static/static/static/docs/terms_privacy/OpenBio_Privacy_Policy.pdf' # URL OF PRIVACY
FUNDING_LOGOS = True # Show the funding logos?
TEST = False # Are we testing the views?
ARGO_EXECUTION_CLIENT_URL = 'argo:///karvdash-'
