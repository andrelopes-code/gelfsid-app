import re
from pathlib import Path

from django.template import base as template_base
from environ import Env

# Adicionar suporte para parsear multilinha em tags de template (GAMBIARRA)
template_base.tag_re = re.compile(template_base.tag_re.pattern, re.DOTALL)

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env('.env')

DEBUG = env.bool('DEBUG')
SECRET_KEY = env.str('SECRET_KEY')


# Chave da API do Graphhopper para calcular distâncias
GRAPHHOPPER_API_KEY = env.str('GRAPHHOPPER_API_KEY', '')


CORS_ALLOW_ALL_ORIGINS = True
SECURE_SSL_REDIRECT = False
X_FRAME_OPTIONS = 'SAMEORIGIN'

ALLOWED_HOSTS = env.str('ALLOWED_HOSTS').split(',')
CSRF_TRUSTED_ORIGINS = env.str('CSRF_TRUSTED_ORIGINS').split(',')


STATIC_URL = '/static/'
STATICFILES_DIRS = [str(BASE_DIR / 'static')]
STATIC_ROOT = str(BASE_DIR / 'staticfiles')
MEDIA_ROOT = str(BASE_DIR / 'media')
MEDIA_URL = '/media/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
ROOT_URLCONF = 'gelfcore.urls'
WSGI_APPLICATION = 'gelfcore.wsgi.application'


INSTALLED_APPS = [
    'admin_interface',
    'colorfield',
    'django_tables2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'corsheaders',
    'gelfmp',
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
                'gelfmp.context.global_context',
            ],
        },
    },
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '',
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


SHELL_PLUS = 'ipython'
SHELL_PLUS_PRINT_SQL = True

IPYTHON_ARGUMENTS = [
    '--ext',
    'django_extensions.management.notebook_extension',
    '--debug',
]
