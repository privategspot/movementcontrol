from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


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
        return reverse("facility-entries-list", kwargs={
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

    class Meta:
        abstract = True


class Employee(AbstractPerson):

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


class AbstractMovementEntry(models.Model):
    """
    Абстрактная модель записи о заезде/отъезде сотрудника.
    Содержит поля, изменения которых необходимо хранить в
    модели 'MovementEntryHistory'.
    """

    ARRIVING = "ARR"
    LEAVING = "LVN"
    TYPES_OF_ENTRY = [
        (ARRIVING, "Заезд"),
        (LEAVING, "Отъезд"),
    ]

    entry_type = models.CharField(
        "Тип записи",
        max_length=3,
        choices=TYPES_OF_ENTRY,
        default=ARRIVING
    )
    employee = models.OneToOneField(
        Employee,
        on_delete=models.RESTRICT,
        null=True,
        verbose_name="Заезжающий/отъезжающий сотрудник"
    )
    scheduled_datetime = models.DateTimeField("Дата и время заезда/отъезда")

    class Meta:
        abstract = True


class MovementEntry(AbstractMovementEntry):
    """
    Запись содержащая информацию о заезде/отъезде
    сотрудников на производственный объект
    """

    facility = models.ForeignKey(
        FacilityObject,
        on_delete=models.CASCADE,
        verbose_name="Производственный объект"
    )
    creator = models.OneToOneField(
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
    def entry_type_humanize(self):
        """
        Метод возвращает человекочитаемую строку,
        определяющую тип списка в именительном падеже
        единственного числа.
        Например: "заезд" или "отъезд".
        """
        arriving_value = self.TYPES_OF_ENTRY[0][1]
        leaving_value = self.TYPES_OF_ENTRY[1][1]

        if self.entry_type == self.ARRIVING:
            entry_type = arriving_value
        else:
            entry_type = leaving_value

        humanize = entry_type.lower()
        return humanize

    @property
    def was_changed(self):
        """
        Возвращает True, если запись была изменена, иначе False
        """
        return True if self.creation_datetime != self.last_modified else False

    def get_absolute_url(self):
        """
        Возвращает url записи
        """
        return reverse("movement-entry", kwargs={
            "facility_slug": self.facility.slug,
            "pk": self.pk,
        })

    def __str__(self):
        datetime = self.scheduled_datetime
        return "Дата %s сотрудника %s: %s.%s.%s %s:%s" % (
            self.entry_type_humanize + "a",
            self.employee.full_name,
            datetime.day,
            datetime.month,
            datetime.year,
            datetime.hour,
            datetime.minute,
        )

    class Meta:
        verbose_name = "Запись о заезде/отъезде"
        verbose_name_plural = "Записи о заездах/отъездах"


class MovementEntryHistory(models.Model):
    """
    История изменений записи
    """

    modified_entry = models.ForeignKey(
        "MovementEntry",
        on_delete=models.CASCADE
    )
    modified_by = models.OneToOneField(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True
    )
    modified_datetime = models.DateTimeField("Время внесения изменений")
    field_name = models.TextField("Имя измененного поля")
    field_type = models.TextField("Тип измененного поля")
    field_old_value = models.TextField("Старое значение поля")
    field_new_value = models.TextField("Новое значение поля")

    class Meta:
        verbose_name = "Состояние записи"
        verbose_name_plural = "Состояния записей"
