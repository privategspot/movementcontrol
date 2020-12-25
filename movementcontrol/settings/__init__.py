# в этом файле необходимо импортировать подходящие настройки
# from .production import *  # настройки для рабочего окружения
from .development import *  # настройки для разработки

try:
    from .local_settings import *
except ImportError:
    pass
