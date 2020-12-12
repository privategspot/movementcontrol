from django.db import models
from django.contrib.auth import get_user_model

from .utils import ChangeMeta


ACTIONS = (
    (ChangeMeta.CREATE_ACTION, "Создание"),
    (ChangeMeta.UPDATE_ACTION, "Изменение"),
    (ChangeMeta.DELETE_ACTION, "Удаление"),
    (ChangeMeta.RESTORE_ACTION, "Восстановление"),
)


class ChangeLogManager(models.Manager):
    """
    Кастомный менеджер для управления объектами модели ChangeLog.
    Модифицирует метод создания объекта
    """

    def get_model_changelogs(self, model: models.Model, model_pk: int):
        """
        Возвращает объект Queryset содержащий исторические записи
        ChangeLog для модели model по первичному ключу model_pk
        """
        queryset = self.filter(model=model)
        queryset = queryset.filter(model_pk=model_pk)


class ChangeLog(models.Model):
    """
    Хранит изменения примененные к модели.
    Изменения хранятся в сериализованном виде.
    """

    class Meta:
        ordering = ("change_datetime",)
        verbose_name = "Историческая запись"
        verbose_name_plural = "Исторические записи"

    objects = ChangeLogManager()

    change_datetime = models.DateTimeField("Дата и время изменения")
    changed_by = models.ManyToManyField(
        get_user_model(),
        verbose_name="Кем изменено"
    )
    action = models.CharField("Тип изменения", choices=ACTIONS, max_length=10)
    model = models.CharField("Имя модели изменяемого объекта", max_length=255)
    model_pk = models.IntegerField("Первичный ключ изменяемого объекта")
    prev_change = models.JSONField(
        "Данные до изменения в формате JSON",
        blank=True,
        null=True,
    )
    post_change = models.JSONField(
        "Измененные данные в формате JSON",
        blank=True,
        null=True,
    )
    comment = models.TextField(
        "Текстовый комментарий",
        blank=True,
        default=""
    )

    def get_datetime_string(self):
        """
        Возвращает строку содержащую дату и время в формате '%d.%m.%Y %H:%M:%S'
        """
        return self.datetime.strftime("%d.%m.%Y %H:%M:%S")
