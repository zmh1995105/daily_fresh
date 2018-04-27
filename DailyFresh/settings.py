"""
Django settings for DailyFresh project.

Generated by 'django-admin startproject' using Django 1.8.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from django.conf.global_settings import DEFAULT_FILE_STORAGE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!yvxu-()-p&#^!a=d29g*b_=txm4$^!6z#f(3-o-2i@e5=*9ra'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'users.User'  # 重新制定user类


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.cart',
    'apps.goods',
    'apps.orders',
    'apps.users',
    'tinymce',  # 使用第三方富文本编辑器
    'haystack',

)

# 配置控件显示样式
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',  # 丰富样式
    'width': 600,
    'height': 400,
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'DailyFresh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'DailyFresh.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {

        'ENGINE': 'django.db.backends.mysql',
         'NAME': "django_dailyfresh",
         'USER': "root",
         'PASSWORD': "chuanzhi",
         'HOST': "localhost",
         'PORT': 3306,

    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# 邮件发送配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'    # 导入邮件模块
EMAIL_HOST = 'smtp.163.com'                 # 邮箱服务器地址（不同公司的邮箱服务器地址不一样）
EMAIL_PORT = 25                             # 邮箱服务器端口（默认都为25）
EMAIL_HOST_USER = 'Jason_zhengminghao@163.com'       # 发件人（天天生鲜官方邮箱账号）
EMAIL_HOST_PASSWORD = 'zmh1995105'           # 邮箱客户端授权码，非邮箱登录密码
EMAIL_FROM = '天天生鲜<Jason_zhengminghao@163.com>'   # 收件人接收到邮件后，显示在‘发件人’中的内容，如下图

# django项目的缓存配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": ""
        }
    }
}

# session数据缓存到Redis中
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# 如果未登录则跳转到如下地址
LOGIN_URL = '/users/login'


MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media')


# 指定使用自定义文件存储类
DEFAULT_FILE_STORAGE = 'utils.fdfs.storage.FdfsStorage'

# 配置haystack框架
HAYSTACK_CONNECTIONS = {
    'default': {
        # 使用whoosh搜索引擎
        'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',
        # 指定生成的索引库保存在哪个目录下
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    }
}

# 当添加、修改、删除了数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# 设置全文检索结果每页显示2条数据
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 2