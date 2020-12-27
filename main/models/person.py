from django.db import models
from django.core import serializers
from django.contrib.auth.models import AbstractUser


# Этот класс существует, т.к. планировалось, что он будет использоваться
# и в Employee, и в User, но Django не позволяет переопределить,
# таким способом, поля first_name и last_name класса AbstractUser
# Т.к. эта проблема, в будущем, может решиться,
# я оставлю класс 'AbstractPerson'
class AbstractPerson(models.Model):

    first_name = models.CharField("Имя", max_length=40)
    last_name = models.CharField("Фамилия", max_length=40)
    patronymic = models.CharField("Отчество", max_length=40, blank=True)
    position = models.CharField("Должность", max_length=100, blank=True)

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
        if self.first_name and self.last_name:
            initials = "%s %s." % (
                self.last_name,
                self.first_name[0],
            )
        else:
            return "*данные отсутсвуют*"
        if self.patronymic:
            initials = initials + self.patronymic[0] + "."
        return initials

    class Meta:
        abstract = True


class Employee(AbstractPerson):

    is_senior = models.BooleanField(
        "Старший",
        default=False,
    )

    def toJSON(self):
        return serializers.serialize("json", [self])

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        permissions = [
            (
                "can_set_is_senior",
                "Право устанавливать поле 'старший'",
            ),
        ]


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
        if self.first_name and self.last_name:
            initials = "%s %s." % (
                self.last_name,
                self.first_name[0],
            )
        else:
            return "*данные отсутсвуют*"
        if self.patronymic:
            initials = initials + self.patronymic[0] + "."
        return initials
