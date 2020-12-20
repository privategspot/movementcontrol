from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

from .history import HistoryMixin
from .facility import FacilityObject
from ..utils import datetime_to_current_tz


class MovementList(models.Model):

    facility = models.ForeignKey(
        FacilityObject,
        on_delete=models.CASCADE,
        verbose_name="Производственный объект"
    )

    ARRIVING = "ARR"
    LEAVING = "LVN"
    TYPES_OF_LIST = [
        (ARRIVING, "Заезд"),
        (LEAVING, "Выезд"),
    ]
    list_type = models.CharField(
        "Тип списка",
        max_length=3,
        choices=TYPES_OF_LIST,
        default=ARRIVING
    )
    scheduled_datetime = models.DateTimeField("Дата и время заезда/выезда")
    creator = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Кем создана"
    )
    creation_datetime = models.DateTimeField(
        "Время создания",
        auto_now_add=True
    )
    last_modified = models.DateTimeField(
        "Время последнего изменения модели",
        auto_now=True
    )
    was_modified = models.BooleanField(
        "Был ли список изменен?",
        default=False
    )
    is_deleted = models.BooleanField(
        "Удалён?",
        default=False
    )
    place = models.CharField(
        "Место выезда/заезда",
        max_length=255,
        blank=True,
    )
    watch = models.CharField(
        "Вахта",
        max_length=255,
        blank=True,
    )

    @property
    def list_type_humanize(self):
        """
        Метод возвращает человекочитаемую строку,
        определяющую тип списка в именительном падеже
        единственного числа.
        Например: "заезд" или "выезд".
        """
        arriving_value = self.TYPES_OF_LIST[0][1]
        leaving_value = self.TYPES_OF_LIST[1][1]

        if self.list_type == self.ARRIVING:
            list_type = arriving_value
        else:
            list_type = leaving_value

        humanize = list_type.lower()
        return humanize

    @property
    def was_changed(self):
        """
        Возвращает True, если запись была изменена, иначе False
        """
        return self.was_modified

    def get_url_kwargs(self):
        return {
            "facility_slug": self.facility.slug,
            "list_id": self.pk,
        }

    def get_absolute_url(self):
        return reverse("movement-list-entries", kwargs=self.get_url_kwargs())

    def get_add_url(self):
        return reverse("movement-lists-add", args=[self.facility.slug])

    def get_delete_url(self):
        return reverse("movement-list-delete", kwargs=self.get_url_kwargs())

    def get_edit_url(self):
        return reverse("movement-list-edit", kwargs=self.get_url_kwargs())

    def get_history_url(self):
        return reverse("movement-list-history", kwargs=self.get_url_kwargs())

    def is_creator(self, user):
        return self.creator == user

    def has_change_perm(self, user):
        is_creator = self.is_creator(user)
        can_change_owned = user.has_perm("main.change_owned_movementlist")
        can_change = user.has_perm("main.change_movementlist")
        return is_creator and can_change_owned or can_change

    def has_delete_perm(self, user):
        is_creator = self.is_creator(user)
        can_delete_owned = user.has_perm("main.delete_owned_movementlist")
        can_delete = user.has_perm("main.delete_movementlist")
        return is_creator and can_delete_owned or can_delete

    def __str__(self):
        return "%s на %s" % (
            self.list_type_humanize.title(),
            datetime_to_current_tz(
                self.scheduled_datetime
            ).strftime("%d.%m.%Y %H:%M"),
        )

    class Meta:

        verbose_name = "Список заездов/выездов"
        verbose_name_plural = "Списки заездов/выездов"

        permissions = [
            (
                "change_owned_movementlist",
                "Право изменения списка созданного пользователем"
            ),
            (
                "delete_owned_movementlist",
                "Право удаления списка созданного пользователем"
            ),
        ]


class MovementListHistory(HistoryMixin):

    modified_list = models.ForeignKey(
        MovementList,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Состояние списка"
        verbose_name_plural = "Состояния списков"
