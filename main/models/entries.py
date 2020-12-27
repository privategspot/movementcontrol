from django.db import models
from django.urls import reverse
from django.core import serializers
from django.contrib.auth import get_user_model

from .person import Employee
from .lists import MovementList
from .history import HistoryMixin


class MovementEntryManager(models.Manager):

    def get_autocomplete_suggestions(self, field):
        entries = super().all().distinct()
        values = entries.values_list("employee__" + field, flat=True)
        users_values = entries.values_list("creator__" + field, flat=True)
        values = list(values) + list(users_values)
        return values

    def get_not_deleted(self):
        return super().all().filter(is_deleted=False)


class MovementEntry(models.Model):
    """
    Запись содержащая информацию о заезде/выезде
    сотрудников на производственный объект
    """

    objects = MovementEntryManager()

    movement_list = models.ForeignKey(
        MovementList,
        on_delete=models.CASCADE,
        verbose_name="Производственный объект"
    )
    employee = models.OneToOneField(
        Employee,
        on_delete=models.RESTRICT,
        null=True,
        verbose_name="Заезжающий/отъезжающий сотрудник"
    )
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
        "Время последнего изменения",
        auto_now=True
    )
    is_deleted = models.BooleanField(
        "Удалён?",
        default=False
    )
    was_modified = models.BooleanField(
        "Был ли список изменен?",
        default=False
    )

    @property
    def was_changed(self):
        """
        Возвращает True, если запись была изменена, иначе False
        """
        return self.was_modified

    def get_url_kwargs(self):
        return {
            "facility_slug": self.movement_list.facility.slug,
            "list_id": self.movement_list.pk,
            "entry_id": self.pk,
        }

    def get_add_url(self):
        kwargs = self.get_url_kwargs()
        del kwargs["entry_id"]
        return reverse(
            "movement-list-entries-add",
            kwargs=kwargs,
        )

    def get_delete_url(self):
        kwargs = self.get_url_kwargs()
        return reverse(
            "movement-list-entry-delete",
            kwargs=kwargs,
        )

    def get_edit_url(self):
        kwargs = self.get_url_kwargs()
        return reverse(
            "movement-list-entry-edit",
            kwargs=kwargs,
        )

    def get_history_url(self):
        kwargs = self.get_url_kwargs()
        return reverse(
            "movement-list-entry-history",
            kwargs=kwargs,
        )

    def is_creator(self, user):
        return self.creator == user

    def has_change_perm(self, user):
        is_creator = self.is_creator(user)
        can_change_owned = user.has_perm("main.change_owned_movemententry")
        can_change = user.has_perm("main.change_movemententry")
        return is_creator and can_change_owned or can_change

    def has_delete_perm(self, user):
        can_delete_owned = user.has_perm("main.delete_owned_movemententry")
        is_creator = self.is_creator(user)
        can_delete = user.has_perm("main.delete_movemententry")
        return is_creator and can_delete_owned or can_delete

    def __str__(self):
        datetime = self.creation_datetime
        return "Время создания %s.%s.%s %s:%s" % (
            datetime.day,
            datetime.month,
            datetime.year,
            datetime.hour,
            datetime.minute,
        )

    class Meta:

        verbose_name = "Запись о заезде/выезде"
        verbose_name_plural = "Записи о заездах/выездах"

        permissions = [
            (
                "change_owned_movemententry",
                "Право изменения записи созданной пользователем"
            ),
            (
                "delete_owned_movemententry",
                "Право удаления записи созданной пользователем"
            ),
        ]


class MovementEntryHistory(HistoryMixin):
    """
    История изменений записи
    """

    modified_entry = models.ForeignKey(
        MovementEntry,
        on_delete=models.CASCADE
    )

    def get_change_states(self):
        prev_state = next(
            serializers.deserialize("json", self.serialized_prev_delta)
        ).object
        post_state = next(
            serializers.deserialize("json", self.serialized_post_delta)
        ).object
        states = {
            "prev_state": prev_state,
            "post_state": post_state,
        }
        return states

    class Meta:
        verbose_name = "Состояние записи"
        verbose_name_plural = "Состояния записей"
