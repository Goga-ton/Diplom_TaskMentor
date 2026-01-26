from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'Mentor.User'

# Allauth настройки (email как логин)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # стандартный
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth
]

# Sites framework
SITE_ID = 1

# Email как USERNAME_FIELD
# ACCOUNT_AUTHENTICATION_METHOD = 'email' # по рекомендации perplexity
ACCOUNT_LOGIN_METHODS = {'email'} # замена верхней строки по рекомендации seepseek
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*'] # вместо ACCOUNT_EMAIL_REQUIRED и ACCOUNT_USERNAME_REQUIRED
# ACCOUNT_EMAIL_REQUIRED = True # по рекомендации perplexity (строку можно удалить а можно оставить для совместивости рекомендации deepseek)
ACCOUNT_EMAIL_VERIFICATION = 'none'  # mandatory для продакшена
# ACCOUNT_USERNAME_REQUIRED = False # по рекомендации perplexity (строку можно удалить а можно оставить для совместивости рекомендации deepseek)
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# Социальный логин
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_STORE_TOKENS = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'Mentor',
# Allauth ВСЕГДА после sites
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    #'social_django', №нужно удалить по рекомендации DeepSeek т.к. дублируется с  'allauth'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # новая строка
]

ROOT_URLCONF = 'TaskMentor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'TaskMentor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

LOGIN_REDIRECT_URL = 'teacher_dashboard'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login'

# Данный код блокирует авторегистрацию Google
SOCIALACCOUNT_AUTO_SIGNUP = False  # авто-регистрация # ← КРИТИЧНО: блокирует авто-регистрацию при значениее = False
# по рекомендации deepseek
# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         'APP': {
#             'client_id': os.getenv('GOOGLE_CLIENT_ID'),
#             'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
#         },
#         'VERIFIED_EMAIL': True,
#         'SCOPE': ['profile', 'email'],
#     }
# }