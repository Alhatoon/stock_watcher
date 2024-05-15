import os
from cassandra.cqlengine import connection
from cassandra.auth import PlainTextAuthProvider
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'changeme')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get('DEBUG', 0)))

ALLOWED_HOSTS = ["localhost", ""]
ALLOWED_HOSTS_ENV = os.environ.get("ALLOWED_HOSTS")
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS.extend(ALLOWED_HOSTS_ENV.split(","))
    
APPEND_SLASH = False
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tracker',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

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
            ],
        },
    },
]

#WSGI_APPLICATION = 'app.app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django_cassandra_engine',
        'NAME': 'stock_watcher_keyspace', 
        'TEST_NAME': 'test_keyspace',
        'OPTIONS': {
            'replication': {
                'strategy_class': 'SimpleStrategy',
                'replication_factor': 1
            }
        }
    }
}

# REST Framework Configuration for Token Authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# Session Configuration for APIs 
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]



# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/static/'
MEDIA_URL = '/static/media/'
STATIC_ROOT = '/vol/web/static'
MEDIA_ROOT = '/vol/web/media'



# TODO: 
# URLs for login and logout
LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'



# SMTP settings for Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'testingmobily@gmail.com' 
EMAIL_HOST_PASSWORD = 'Toon_1234'


# CQLENG_ALLOW_SCHEMA_MANAGEMENT 
os.environ['CQLENG_ALLOW_SCHEMA_MANAGEMENT'] = '1'


# Replace these with your actual Cassandra credentials and host
CASSANDRA_HOSTS = ['db', 'localhost','172.25.0.2', '127.0.0.1', '::1']
CASSANDRA_KEYSPACE = 'stock_watcher_keyspace'
CASSANDRA_USERNAME = 'cassandra'
CASSANDRA_PASSWORD = 'cassandra'

auth_provider = PlainTextAuthProvider(username=CASSANDRA_USERNAME, password=CASSANDRA_PASSWORD)
connection.setup(CASSANDRA_HOSTS, CASSANDRA_KEYSPACE, auth_provider=auth_provider)

# Issue with request limit size
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024  # 20 MB