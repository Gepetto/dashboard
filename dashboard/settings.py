import os
from pathlib import Path

PROJECT = 'dashboard'
PROJECT_VERBOSE = PROJECT.replace('_', ' ').title()
PROJECT_SLUG = PROJECT.replace('_', '-')
SELF_MAIL = False
DOMAIN_NAME = os.environ.get('DOMAIN_NAME', 'local')
ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOST', f'{PROJECT_SLUG}.{DOMAIN_NAME}')]
ALLOWED_HOSTS += [f'www.{host}' for host in ALLOWED_HOSTS]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'True').lower() == 'true'
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'False').lower() == 'true'
if EMAIL_USE_SSL and EMAIL_USE_TLS:  # pragma: no cover
    raise ValueError('you must not set both EMAIL_USE_{TLS,SSL}')
EMAIL_HOST = os.environ.get('EMAIL_HOST', f'smtp.{DOMAIN_NAME}')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USER = os.environ.get('EMAIL_USER', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 465 if EMAIL_USE_SSL else 587 if EMAIL_USE_TLS else 25))
EMAIL_FQDN = os.environ.get('EMAIL_FQDN', ALLOWED_HOSTS[0] if SELF_MAIL else DOMAIN_NAME)
EMAIL_HOST_USER = f'{EMAIL_USER}@{EMAIL_FQDN}'
SERVER_EMAIL = f'{EMAIL_USER}+{PROJECT}@{EMAIL_FQDN}'
DEFAULT_FROM_EMAIL = f'{PROJECT_VERBOSE} <{EMAIL_USER}@{EMAIL_FQDN}>'
EMAIL_BACKEND = 'django.core.mail.backends.%s' % ('filebased.EmailBackend' if DEBUG else 'smtp.EmailBackend')
EMAIL_SUBJECT_PREFIX = f'[{PROJECT_VERBOSE}] '

ADMINS = ((os.environ.get('ADMIN_NAME',
                          f'{PROJECT_VERBOSE} webmaster'), os.environ.get('ADMIN_MAIL', f'webmaster@{DOMAIN_NAME}')), )

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'rest_framework',
    'django_tables2',
    'django_filters',
    'bootstrap4',
    'ndh',
    'rainboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dashboard.middleware.LAASPermsMiddleware',
]

ROOT_URLCONF = f'{PROJECT}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = f'{PROJECT}.wsgi.application'

DB = os.environ.get('DB', 'db.sqlite3')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, DB),
    }
}
if DB == 'postgres':  # pragma: no cover
    DATABASES['default'].update(
        ENGINE='django.db.backends.postgresql',
        NAME=os.environ.get('POSTGRES_DB', DB),
        USER=os.environ.get('POSTGRES_USER', DB),
        HOST=os.environ.get('POSTGRES_HOST', DB),
        PASSWORD=os.environ['POSTGRES_PASSWORD'],
    )

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

LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'fr')
TIME_ZONE = os.environ.get('TIME_ZONE', 'Europe/Paris')
USE_I18N = True
USE_L10N = True
USE_TZ = True

SITE_ID = int(os.environ.get('SITE_ID', 1))

MEDIA_ROOT = '/srv/media/'
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
STATIC_ROOT = '/srv/static/'

if os.environ.get('MEMCACHED', 'False').lower() == 'true':  # pragma: no cover
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': 'memcached:11211',
        }
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend', ),
}

DJANGO_TABLES2_TEMPLATE = 'rainboard/tables.html'
RAINBOARD_DATA = Path('/srv/dashboard')
RAINBOARD_GITS = RAINBOARD_DATA / 'repositories'
RAINBOARD_RPKG = RAINBOARD_DATA / 'robotpkg'
PRIVATE_REGISTRY = 'gepgitlab.laas.fr:4567'
PUBLIC_REGISTRY = 'memmos.laas.fr:5000'
GITHUB_USER = 'hrp2-14'

AUTHENTICATION_BACKENDS = ["django_auth_ldap.backend.LDAPBackend"]

AUTH_LDAP_SERVER_URI = "ldap://ldap.laas.fr"
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=laas,dc=fr"
AUTH_LDAP_START_TLS = True
AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn", "email": "laas-mainMail"}

LAAS_NETWORKS = ['140.93.0.0/21', '2001:660:6602:4::/64']
