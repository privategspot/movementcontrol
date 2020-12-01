import os

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth.models import Group, Permission
from main.models import FacilityObject


COMMON_PERMS = [
    "view_facilityobject",
    "view_movementlist",
    "view_movemententry",
    "view_movementlisthistory",
    "view_movemententryhistory",
]

COMMANDANT_GROUP_PERMS = [
    "add_movementlist",
    "change_movementlist",
    "delete_movementlist",
    "add_movemententry",
    "change_movemententry",
    "delete_movemententry",
] + COMMON_PERMS

MANAGER_GROUP_PERMS = [
    "add_movemententry",
    "change_owned_movemententry",
    "delete_owned_movemententry",
] + COMMON_PERMS


class Command(BaseCommand):
    help = """
    Creates a migration file, applies migrations,
    initializes the database by creating base user groups and superuser
    """

    def handle(self, *args, **kwargs):
        # Создаем файл миграций
        call_command("makemigrations")
        self.stdout.write(self.style.SUCCESS(
            "Migration file created successfully"
        ))
        # Применяем миграции
        call_command("migrate")
        self.stdout.write(self.style.SUCCESS(
            "Migrations applied successfully"
        ))
        # Добавляем суперпользователя
        os.environ["DJANGO_SUPERUSER_PASSWORD"] = "admin1"
        call_command("createsuperuser", username="admin", email="")
        self.stdout.write(self.style.WARNING(
            "Immediately after creating the superuser, change its password to a secure one!"
        ))
        os.environ.pop("DJANGO_SUPERUSER_PASSWORD")
        # Создаём базовые группы пользователей
        self.stdout.write("Creating user groups...")
        try:
            commandant_group, created = Group.objects.get_or_create(
                name="Комендант"
            )
            if not created:
                for perm in COMMANDANT_GROUP_PERMS:
                    perm_obj = Permission.objects.get(name=perm)
                    commandant_group.permissions.add(perm_obj)

            manager_group, created = Group.objects.get_or_create(
                name="Руководитель"
            )
            if not created:
                for perm in MANAGER_GROUP_PERMS:
                    perm_obj = Permission.objects.get(name=perm)
                    manager_group.permissions.add(perm_obj)
        except Group.DoesNotExist:
            raise CommandError("Group does not exist")
        self.stdout.write(self.style.SUCCESS("Groups created"))

        self.stdout.write("Creating a default manufacturing facility...")
        # Создаём производественный объект по умолчанию
        try:
            FacilityObject.objects.create(
                name="Рудник Шануч",
                slug="shanuch-mine"
            )
        except FacilityObject.DoesNotExist:
            raise CommandError("FacilityObject does not exist")
        self.stdout.write(self.style.SUCCESS("Production facility created"))

        self.stdout.write(self.style.SUCCESS("Init complete"))
