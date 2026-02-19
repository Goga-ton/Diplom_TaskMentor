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
DEBUG = True # Локальный запуск, False для Продакшина и там еще кучу настроек нужно будет делать
DEBUG_CALENDAR_SYNC = False  # отладочные print'ы для Google Calendar sync False выключит принты

ALLOWED_HOSTS = [] #если DEBUG = False тогда в скобках ("127.0.0.1", "localhost"), если True тогда ничего

AUTH_USER_MODEL = 'Mentor.User'

# Allauth настройки (email как логин)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # стандартный
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth
]

# Sites framework
SITE_ID = 1

# Allauth настройки
ACCOUNT_AUTHENTICATION_METHOD = 'email'      # Используем email для входа
ACCOUNT_EMAIL_REQUIRED = True                # Email обязателен
ACCOUNT_USERNAME_REQUIRED = False            # Не используем username
ACCOUNT_USER_MODEL_USERNAME_FIELD = None     # Указываем, что username нет ← ОСТАВЛЯЕМ
ACCOUNT_EMAIL_VERIFICATION = 'none'          # 'mandatory' для продакшена
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']

# Социальный логин
SOCIALACCOUNT_QUERY_EMAIL = True # Запрашивать email у социального провайдера (Google). Без этого может не получить email пользователя.
SOCIALACCOUNT_STORE_TOKENS = True # Важно для токенов календаря. Сохранять OAuth токены в базу данных. Без этого Allauth не сохранит access_token и refresh_token.
SOCIALACCOUNT_AUTO_SIGNUP = False  # Автоматически создавать пользователя при первом входе через соцсеть. Если False - потребуется дополнительная регистрация после OAuth.
SOCIALACCOUNT_EMAIL_REQUIRED = True #Email обязателен для социальных аккаунтов. Если у провайдера нет email - вход будет отклонен.
SOCIALACCOUNT_ADAPTER = 'Mentor.adapters.CustomSocialAccountAdapter'
ACCOUNT_ADAPTER = "Mentor.adapters.CustomAccountAdapter"

#Для мобильного приложения
FCM_ENABLED = os.getenv("FCM_ENABLED", "false").lower() == "true"
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "")

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

    'webpush',
    'django_celery_beat',
# Allauth ВСЕГДА после sites
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

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
                'Mentor.context_processors.webpush_settings',
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

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / 'staticfiles' # создает каталог staticfiles для Продакшена

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login'

WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": os.getenv("WEBPUSH_PUBLIC_KEY"),
    "VAPID_PRIVATE_KEY": os.getenv("WEBPUSH_PRIVATE_KEY"),
    "VAPID_ADMIN_EMAIL": "admin@taskmentor.ru"
}
# Celery (Redis брокер)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Планировщик
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'openid',
            'email',
            'profile',
            'https://www.googleapis.com/auth/calendar',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
            'prompt': 'consent',
        }
    }
}

