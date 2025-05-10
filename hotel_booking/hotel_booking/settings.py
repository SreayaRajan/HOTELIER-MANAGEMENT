
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-)(1)ocqux@e_z&*9^53j0c=%0a3*&d$+y@jj997*!bpf@wfqc4'
DEBUG = True
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.locale.LocaleMiddleware', 

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hotel_booking.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),  # Global templates directory
            os.path.join(BASE_DIR, 'home', 'templates'),  # Your current setup
        ],
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

WSGI_APPLICATION = 'hotel_booking.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql",
        'NAME': "Hotelier",
        "USER":"postgres",
        "PASSWORD":"7654321",
        "HOST":"localhost",
        "PORT":"5432"
    }
}

AUTHENTICATION_BACKENDS = [
    # 'home.auth_backend.UserProfileBackend',  # Add this line
     'home.auth_backends.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',  # Keep default backend
]

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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'home/static')]
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
AUTH_USER_MODEL = 'home.UserProfile'




LOGIN_URL = '/login/' 
LOGIN_REDIRECT_URL = '/hotel_room/'
LOGOUT_REDIRECT_URL = '/login/' 



RAZORPAY_KEY_ID = "rzp_test_d5VCv4MOwkIpcU"
RAZORPAY_KEY_SECRET = "OXxDDHSLPDiM9yvqbd1SAFdN"


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com' 
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'sreayarajan75@gmail.com'
EMAIL_HOST_PASSWORD = 'kouy inwf pahj vejt'

LANGUAGE_CODE = 'en'  # Default is English

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('ml', 'Malayalam'),
    ('hi', 'Hindi'),
    ('kn', 'Kannada'),
    ('ta', 'Tamil'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
