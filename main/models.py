from django.db import models
from django.urls import reverse
from django.core import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from .utils import datetime_to_current_tz


class FacilityObject(models.Model):

    name = models.CharField(
        "Название производственного объекта",
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        "Уникальная строка идентификатор (slug)",
        max_length=100,
        unique=True
    )

    def get_absolute_url(self):
        return reverse("movement-lists", kwargs={
            "facility_slug": self.slug,
        })

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Производственный объект"
        verbose_name_plural = "Производственные объекты"


# Этот класс существует, т.к. планировалось, что он будет использоваться
# и в Employee, и в User, но Django не позволяет переопределить,
# таким способом, поля first_name и last_name класса AbstractUser
# Т.к. эта проблема, в будущем, может решиться,
# я оставлю класс 'AbstractPerson'
class AbstractPerson(models.Model):

    first_name = models.CharField("Имя", max_length=40)
    last_name = models.CharField("Фамилия", max_length=40)
    patronymic = models.CharField("Отчество", max_length=40, blank=True)
    position = models.CharField("Должность", max_length=100)

    @property
    def full_name(self):
        full_name = "%s %s %s" % (
            self.last_name,
            self.first_name,
            self.patronymic,
        )
        full_name = full_name.strip()
        return full_name

    @property
    def initials(self):
        initials = "%s %s." % (
            self.last_name,
            self.first_name[0],
        )
        if len(self.patronymic):
            initials = initials + self.patronymic[0] + "."
        return initials

    class Meta:
        abstract = True


class Employee(AbstractPerson):

    def toJSON(self):
        return serializers.serialize("json", [self])
    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class User(AbstractUser):

    first_name = models.CharField("Имя", max_length=40)
    last_name = models.CharField("Фамилия", max_length=40)
    patronymic = models.CharField("Отчество", max_length=40, blank=True)
    position = models.CharField("Должность", max_length=100)

    @property
    def full_name(self):
        full_name = "%s %s %s" % (
            self.last_name,
            self.first_name,
            self.patronymic,
        )
        full_name = full_name.strip()
        return full_name

    @property
    def initials(self):
        initials = "%s %s." % (
            self.last_name,
            self.first_name[0],
        )
        if len(self.patronymic):
            initials = initials + self.patronymic[0] + "."
        return initials


class HistoryMixin(models.Model):

    modified_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True
    )
    modified_datetime = models.DateTimeField("Время внесения изменений")
    serialized_prev_delta = models.TextField("Данные до изменения")
    serialized_post_delta = models.TextField("Данные после изменения")

    class Meta:
        abstract = True


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
    scheduled_datetime = models.DateTimeField("Дата и время заезда/отъезда")
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

    @property
    def list_type_humanize(self):
        """
        Метод возвращает человекочитаемую строку,
        определяющую тип списка в именительном падеже
        единственного числа.
        Например: "заезд" или "отъезд".
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
        return True if self.creation_datetime != self.last_modified else False

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
        is_creator = self.is_creator(user) and user.has_perm(
            "main.change_owned_movementlist"
        )
        return is_creator or user.has_perm("main.change_movementlist")

    def has_delete_perm(self, user):
        is_creator = self.is_creator(user) and user.has_perm(
            "main.delete_owned_movementlist"
        )
        return is_creator or user.has_perm("main.delete_movementlist")

    def __str__(self):
        return "%s на %s" % (
            self.list_type_humanize.title(),
            datetime_to_current_tz(
                self.scheduled_datetime
            ).strftime("%d.%m.%Y"),
        )

    class Meta:

        verbose_name = "Список заездов/отъездов"
        verbose_name_plural = "Списки заездов/отъездов"

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


class MovementEntryManager(models.Manager):

    def get_autocomplete_suggestions(self, field):
        entries = super().all().distinct()
        values = entries.values_list("employee__" + field, flat=True)
        return values


class MovementEntry(models.Model):
    """
    Запись содержащая информацию о заезде/отъезде
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

    @property
    def was_changed(self):
        """
        Возвращает True, если запись была изменена, иначе False
        """
        return True if self.creation_datetime != self.last_modified else False

    def get_url_kwargs(self):
        return {
            "facility_slug": self.movement_list.facility.slug,
            "list_id": self.movement_list.pk,
            "entry_id": self.pk,
        }

    def get_add_url(self):
        return reverse(
            "movement-list-entries-add",
            args=[self.movement_list.facility.slug, self.movement_list.pk]
        )

    def get_delete_url(self):
        return reverse(
            "movement-list-entry-delete",
            kwargs=self.get_url_kwargs()
        )

    def get_edit_url(self):
        return reverse(
            "movement-list-entry-edit",
            kwargs=self.get_url_kwargs()
        )

    def get_history_url(self):
        return reverse(
            "movement-list-entry-history",
            kwargs=self.get_url_kwargs()
        )

    def is_creator(self, user):
        return self.creator == user

    def has_change_perm(self, user):
        is_creator = self.is_creator(user)
        has_perm = user.has_perm("main.change_owned_movemententry")
        print(has_perm)
        return is_creator and has_perm or user.has_perm(
            "main.change_movemententry"
        )

    def has_delete_perm(self, user):
        is_creator = self.is_creator(user) and user.has_perm(
            "main.delete_owned_movemententry"
        )
        return is_creator or user.has_perm("main.delete_movemententry")

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

        verbose_name = "Запись о заезде/отъезде"
        verbose_name_plural = "Записи о заездах/отъездах"

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
