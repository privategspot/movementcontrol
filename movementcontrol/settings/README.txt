Для корректной работы в файле local_settings.py необходимо указать следующие настройки:
    - DATABASES = {
        'default': {
            'ENGINE': 'движок(напр. "django.db.backends.postgresql_psycopg2" для PostgreSQL)',
            'NAME': 'имя_базы_данных',
            'USER': 'имя-пользователя',
            'PASSWORD': 'пароль-пользователя',
            'HOST': 'хост',
            'PORT': 'порт-хоста',
        }
    }
    - SECRET_KEY = "секретный-ключ-Django"

Подробнее про настройки можно прочесть по следующей ссылки:
https://docs.djangoproject.com/en/dev/ref/settings/

Файл local_settings не должен быть доступен публично,
т.к. предназначен для настроек, содержащих пароли и ключи шифрования 
