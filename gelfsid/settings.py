import re
from pathlib import Path

from django.template import base as template_base
from django.templatetags.static import static
from environ import Env

# ! Adicionar suporte para multilinha em tags de template (GAMBIARRA)
template_base.tag_re = re.compile(template_base.tag_re.pattern, re.DOTALL)

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env('.env')

DEBUG = env.bool('DEBUG', False)
SECRET_KEY = env.str('SECRET_KEY', 'secret')
GRAPHHOPPER_API_KEY = env.str('GRAPHHOPPER_API_KEY', '')

STATES_AND_CITIES_PATH = 'static/data/states_and_cities.json'
CORS_ALLOW_ALL_ORIGINS = True
SECURE_SSL_REDIRECT = False
ALLOWED_HOSTS = ['*']

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATIC_FILES_BASE_URL = env.str('STATIC_FILES_BASE_URL')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'corsheaders',
    'map',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gelfsid.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'map.context.global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'gelfsid.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

UNFOLD = {
    'SITE_TITLE': 'GELFSID ADMIN PANEL',
    'SITE_HEADER': 'GELFSID ADMIN',
    'SITE_URL': '/',
    'THEME': 'dark',
    'COLORS': {
        'font': {
            'subtle-light': '107 114 128',
            'subtle-dark': '156 163 175',
            'default-light': '75 85 99',
            'default-dark': '209 213 219',
            'important-light': '17 24 39',
            'important-dark': '243 244 246',
        },
        'primary': {
            '50': '214 131 103',
            '100': '214 131 103',
            '200': '214 131 103',
            '300': '214 131 103',
            '400': '214 131 103',
            '500': '214 131 103',
            '600': '214 131 103',
            '700': '214 131 103',
            '800': '214 131 103',
            '900': '214 131 103',
            '950': '214 131 103',
        },
    },
    'STYLES': [
        lambda request: static('css/unfold_style.css'),
    ],
}
