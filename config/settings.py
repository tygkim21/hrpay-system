"""
Django settings for hrpay-system.

PyMySQL is installed as MySQLdb driver in config/__init__.py.
"""
from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 'django-insecure-p(2nvh(7zxn^bvukq^q!7r$yj9c*yldsyl=h5)#csz*d07j7ky'
# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True
#ALLOWED_HOSTS = []

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG      = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 서드파티
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',

    # 프로젝트 앱
    'apps.accounts',
    'apps.employees',
    'apps.attendance',
    'apps.payroll',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',              # 최상단 필수
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',          # 정적 파일 (운영)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.mysql',
        'NAME'    : os.getenv('DB_NAME'),
        'USER'    : os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST'    : os.getenv('DB_HOST', '127.0.0.1'),
        'PORT'    : os.getenv('DB_PORT', '3306'),
        'OPTIONS' : {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ── DRF 설정 
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',  # 기본: 인증 필수
    ),
    'DEFAULT_PAGINATION_CLASS' : 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE'                : 20,
}

# ── JWT 설정 
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME' : timedelta(
        minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME', 30))
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME', 7))
    ),
    'ROTATE_REFRESH_TOKENS' : True,   # 갱신 시 Refresh도 새로 발급
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES'     : ('Bearer',),
}

# ── CORS 설정 ─────────────────────────────────────────
# 개발: localhost:3000  |  운영: .env의 CORS_ALLOWED_ORIGINS에 추가
_cors_default = 'http://localhost:3000,http://127.0.0.1:3000'
CORS_ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv('CORS_ALLOWED_ORIGINS', _cors_default).split(',') if o.strip()
]
CORS_ALLOW_CREDENTIALS = True


# ── 커스텀 User 모델 ───────────────────────────────────
AUTH_USER_MODEL = 'accounts.CustomUser'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE     = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'          # collectstatic 수집 경로

# whitenoise: 정적 파일 압축 + 해시 캐싱 (운영 환경)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
