from pathlib import Path

from django.templatetags.static import static
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool
    SECRET_KEY: str

    GRAPHHOPPER_API_KEY: str = ''
    CITIES_STATES_PATH: str = 'src/static/data/states_cities.json'

    class Config:
        env_file = '.env'


settings = Settings()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = settings.SECRET_KEY
DEBUG = settings.DEBUG

ALLOWED_HOSTS = []


if settings.DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    ALLOWED_HOSTS = ['*']

CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

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


STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


UNFOLD = {
    'SITE_TITLE': 'GELFSID ADMIN PANEL',
    'SITE_HEADER': 'GELFSID ADMIN',
    'SITE_URL': '/',
    'SHOW_HISTORY': True,
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
