import os
from django.contrib.messages import constants as messages


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = os.environ.get("SECRET_KEY")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    'maintenance_mode',
    'soccer.apps.SoccerConfig',
    'captcha',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'soccer.middlewares.IpRestrictMiddleware',
    'maintenance_mode.middleware.MaintenanceModeMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

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
                'myproject.context_processors.common',
                'maintenance_mode.context_processors.maintenance_mode',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

AUTH_USER_MODEL = 'soccer.CustomUser'

MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
MAINTENANCE_MODE_IGNORE_SUPERUSER = True

EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS")

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL")

# Google Tags
GOOGLE_ADSENSE_PUBLISHER_ID = os.environ.get("GOOGLE_ADSENSE_PUBLISHER_ID")
GOOGLE_ANALYTICS_TRACKING_ID = os.environ.get("GOOGLE_ANALYTICS_TRACKING_ID")

AUTHENTICATION_BACKENDS = (
    #メールアドレス認証
    'allauth.account.auth_backends.AuthenticationBackend',
    #ユーザー名認証
    'django.contrib.auth.backends.ModelBackend',
)
#メールアドレス認証に変更する設定
ACCOUNT_AUTHENTICATION_METHOD = 'email'
#ユーザー名の入力を必要とする設定
ACCOUNT_USERNAME_REQUIRED = True
#サインアップにメールアドレス確認をはさむよう設定
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
#ログイン/ログアウト後の遷移先を設定
LOGIN_REDIRECT_URL = 'soccer:user_detail'
ACCOUNT_LOGOUT_REDIRECT_URL = '/login/'
#ログアウトリンクのクリック一発でログアウトする設定
ACCOUNT_LOGOUT_ON_GET = True

LOGIN_URL = '/login/'

ACTIVATION_EXPIRED_DAYS = 1

PROTOCOL = os.environ.get("PROTOCOL")
DOMAIN = os.environ.get("DOMAIN")
DJANGO_ADMIN_URL = os.environ.get("DJANGO_ADMIN_URL", "admin/")

TWEEPY_BEARER_TOKEN = os.environ.get("TWEEPY_BEARER_TOKEN")
TWEEPY_CONSUMER_KEY = os.environ.get("TWEEPY_CONSUMER_KEY")
TWEEPY_CONSUMER_SECRET = os.environ.get("TWEEPY_CONSUMER_SECRET")
TWEEPY_ACCESS_TOKEN = os.environ.get("TWEEPY_ACCESS_TOKEN")
TWEEPY_ACCESS_TOKEN_SECRET = os.environ.get("TWEEPY_ACCESS_TOKEN_SECRET")