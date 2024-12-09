from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') == 'True'

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'social_django',
    'drf_yasg',
    'users',
    'authentication',
    'workspaces',
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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'core.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_DB = os.getenv('REDIS_DB', 0)

# cache setting
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}



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

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'core.utils.exception_filter.custom_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # other authentication classes if needed
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),  # Example: 7 days
    'REFRESH_TOKEN_LIFETIME': timedelta(weeks=52*30),     # 30 years approx.
    'SIGNING_KEY': os.getenv('JWT_SECRET_KEY')
}

# BASE_URL setting
BASE_URL = os.getenv('BASE_URL')
FRONTEND_BASE_URL=os.getenv('FRONTEND_BASE_URL')

# RabbitMQ settings
RABBITMQ_USER = os.environ.get('RABBITMQ_USER')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD')
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', '5672'))
RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE')
RABBITMQ_EMAIL_VERIFICATION_QUEUE = os.getenv('RABBITMQ_EMAIL_VERIFICATION_QUEUE')
RABBITMQ_EMAIL_VERIFICATION_ROUTING_KEY = os.getenv('RABBITMQ_EMAIL_VERIFICATION_ROUTING_KEY')
RABBITMQ_WORKSPACE_INVITE_QUEUE = os.getenv('RABBITMQ_WORKSPACE_INVITE_QUEUE')
RABBITMQ_WORKSPACE_INVITE_ROUTING_KEY = os.getenv('RABBITMQ_WORKSPACE_INVITE_ROUTING_KEY')

print(RABBITMQ_HOST, RABBITMQ_PORT, 'RABBITMQ HOST')
print(RABBITMQ_USER, RABBITMQ_PASSWORD, 'RABBITMQ USER')
print(RABBITMQ_EXCHANGE, 'RABBITMQ_EXCHANGE')
print(RABBITMQ_EMAIL_VERIFICATION_QUEUE, RABBITMQ_EMAIL_VERIFICATION_ROUTING_KEY, 'RABBITMQ_EMAIL_VERIFICATION_QUEUE')
print(RABBITMQ_WORKSPACE_INVITE_QUEUE, RABBITMQ_WORKSPACE_INVITE_ROUTING_KEY, 'RABBITMQ_WORKSPACE_INVITE_QUEUE')

# for email service
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# google login config
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',  # Keep the default authentication backend
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('GOOGLE_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_LOGIN_REDIRECT_ENDPOINT = os.getenv('GOOGLE_LOGIN_REDIRECT_ENDPOINT')


APPEND_SLASH = True

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Custom Model
AUTH_USER_MODEL = 'users.User'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
