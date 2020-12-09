from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models import FacilityObject, Employee, MovementList, MovementEntry
from ..utils import datetime_to_current_tz


class FacilityObjectModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        FacilityObject.objects.create(name="Рудник Шануч", slug="shanuch-mine")

    def setUp(self):
        self.facility = FacilityObject.objects.get(pk=1)

    def test_name_label(self):
        field_label = self.facility._meta.get_field("name").verbose_name
        self.assertEqual(field_label, "Название производственного объекта")

    def test_slug_label(self):
        field_label = self.facility._meta.get_field("slug").verbose_name
        self.assertEqual(field_label, "Уникальная строка идентификатор (slug)")

    def test_name_max_length(self):
        max_length = self.facility._meta.get_field("name").max_length
        self.assertEqual(max_length, 100)

    def test_slug_max_length(self):
        max_length = self.facility._meta.get_field("slug").max_length
        self.assertEqual(max_length, 100)

    def test_verbose_name_is_correct(self):
        verbose_name = self.facility._meta.verbose_name
        self.assertEqual(verbose_name, "Производственный объект")

    def test_verbose_name_plural_is_correct(self):
        verbose_name_plural = self.facility._meta.verbose_name_plural
        self.assertEqual(verbose_name_plural, "Производственные объекты")

    def test_get_absolute_url_is_correct(self):
        absolute_url = self.facility.get_absolute_url()
        reference_absolute_url = reverse("movement-lists", kwargs={
            "facility_slug": "shanuch-mine"
        })
        self.assertEqual(absolute_url, reference_absolute_url)

    def test_object_name_is_model_name_field(self):
        facility_name = self.facility.name
        self.assertEqual(facility_name, str(self.facility))


class EmployeeModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Employee.objects.create(
            first_name="Пётр",
            last_name="Иванов",
            patronymic="Васильевич",
            position="Младший программист"
        )

    def setUp(self):
        self.employee = Employee.objects.get(pk=1)

    def test_first_name_label(self):
        label = self.employee._meta.get_field("first_name").verbose_name
        self.assertEqual(label, "Имя")

    def test_first_name_max_length(self):
        max_length = self.employee._meta.get_field("first_name").max_length
        self.assertEqual(max_length, 40)

    def test_last_name_label(self):
        label = self.employee._meta.get_field("last_name").verbose_name
        self.assertEqual(label, "Фамилия")

    def test_last_name_max_length(self):
        max_length = self.employee._meta.get_field("last_name").max_length
        self.assertEqual(max_length, 40)

    def test_patronymic_label(self):
        label = self.employee._meta.get_field("patronymic").verbose_name
        self.assertEqual(label, "Отчество")

    def test_patronymic_max_length(self):
        max_length = self.employee._meta.get_field("patronymic").max_length
        self.assertEqual(max_length, 40)

    def test_patronymic_can_be_blank(self):
        blank = self.employee._meta.get_field("patronymic").blank
        self.assertEqual(blank, True)

    def test_position_label(self):
        label = self.employee._meta.get_field("position").verbose_name
        self.assertEqual(label, "Должность")

    def test_position_max_length(self):
        max_length = self.employee._meta.get_field("position").max_length
        self.assertEqual(max_length, 100)

    def test_position_can_be_blank(self):
        blank = self.employee._meta.get_field("position").blank
        self.assertEqual(blank, True)

    def test_full_name_property(self):
        full_name = self.employee.full_name
        self.assertEqual(full_name, "Иванов Пётр Васильевич")

    def test_initials_property(self):
        initials = self.employee.initials
        self.assertEqual(initials, "Иванов П.В.")

    def test_verbose_name(self):
        verbose_name = self.employee._meta.verbose_name
        self.assertEqual(verbose_name, "Сотрудник")

    def test_verbose_name_plural(self):
        verbose_name_plural = self.employee._meta.verbose_name_plural
        self.assertEqual(verbose_name_plural, "Сотрудники")


class MovementListModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        facility = FacilityObject.objects.create(
            name="Рудник Шануч",
            slug="shanuch-mine"
        )
        creator = get_user_model().objects.create_user(
            username="user1",
            email="user1@mail.com",
            password="user1pwd",
        )
        creator.first_name = "Александр"
        creator.last_name = "Бобров"
        creator.patronymic = "Сергеевич"
        creator.position = "Электрик"
        creator.save()
        MovementList.objects.create(
            facility=facility,
            list_type=MovementList.ARRIVING,
            scheduled_datetime=timezone.now(),
            creator=creator,
        )

    def setUp(self):
        self.facility = FacilityObject.objects.get(slug="shanuch-mine")
        self.creator = get_user_model().objects.get(pk=1)
        self.movement_list = MovementList.objects.get(pk=1)

    def test_verbose_name(self):
        verbose_name = self.movement_list._meta.verbose_name
        self.assertEqual("Список заездов/выездов", verbose_name)

    def test_verbose_name_plural(self):
        verbose_name_plural = self.movement_list._meta.verbose_name_plural
        self.assertEqual("Списки заездов/выездов", verbose_name_plural)

    def test_facility_field(self):
        facility = self.movement_list.facility
        self.assertEqual(facility, self.facility)

    def test_facility_field_verbose_name(self):
        verbose_name = self.movement_list.facility._meta.verbose_name
        self.assertEqual(verbose_name, "Производственный объект")

    def test_creator(self):
        creator = self.movement_list.creator
        self.assertEqual(creator, self.creator)

    def test_list_type_field(self):
        list_type = self.movement_list.list_type
        self.assertEqual(list_type, self.movement_list.ARRIVING)

    def test_list_type_humanize_property(self):
        list_type_humanize = self.movement_list.list_type_humanize
        self.assertNotEqual(list_type_humanize, "выезд")
        self.assertEqual(list_type_humanize, "заезд")

    def test_was_changed_property(self):
        was_changed = self.movement_list.was_changed
        self.assertFalse(was_changed)

    def test_get_url_kwargs_method(self):
        url_kwargs = self.movement_list.get_url_kwargs()
        url_kwargs_keys = url_kwargs.keys()
        self.assertIsInstance(url_kwargs, dict)
        self.assertIn("facility_slug", list(url_kwargs_keys))
        self.assertIn("list_id", list(url_kwargs_keys))
        self.assertEqual(
            type(url_kwargs["facility_slug"]),
            str,
        )
        self.assertEqual(
            type(url_kwargs["list_id"]),
            int,
        )

    def test_get_absolute_url_method(self):
        url_name = "movement-list-entries"
        reference_absolute_url = reverse(
            url_name,
            kwargs={
                "facility_slug": self.movement_list.facility.slug,
                "list_id": self.movement_list.pk,
            }
        )
        absolute_url = self.movement_list.get_absolute_url()
        self.assertEqual(reference_absolute_url, absolute_url)

    def test_get_add_url_method(self):
        url_name = "movement-lists-add"
        reference_add_url = reverse(
            url_name,
            kwargs={
                "facility_slug": self.movement_list.facility.slug,
            }
        )
        add_url = self.movement_list.get_add_url()
        self.assertEqual(reference_add_url, add_url)

    def test_get_delete_url_method(self):
        url_name = "movement-list-delete"
        reference_delete_url = reverse(
            url_name,
            kwargs={
                "facility_slug": self.movement_list.facility.slug,
                "list_id": self.movement_list.pk,
            }
        )
        delete_url = self.movement_list.get_delete_url()
        self.assertEqual(reference_delete_url, delete_url)

    def test_get_edit_url_method(self):
        url_name = "movement-list-edit"
        reference_edit_url = reverse(
            url_name,
            kwargs={
                "facility_slug": self.movement_list.facility.slug,
                "list_id": self.movement_list.pk,
            }
        )
        edit_url = self.movement_list.get_edit_url()
        self.assertEqual(reference_edit_url, edit_url)

    def test_get_history_url_method(self):
        url_name = "movement-list-history"
        reference_history_url = reverse(
            url_name,
            kwargs={
                "facility_slug": self.movement_list.facility.slug,
                "list_id": self.movement_list.pk,
            }
        )
        history_url = self.movement_list.get_history_url()
        self.assertEqual(reference_history_url, history_url)

    def test_is_creator_method(self):
        creator = self.creator
        self.assertTrue(self.movement_list.is_creator(creator))

    def test_has_change_perm_method(self):
        creator = self.movement_list.creator
        has_change_perm = self.movement_list.has_change_perm(creator)
        self.assertFalse(has_change_perm)

    def test_has_delete_perm_method(self):
        creator = self.movement_list.creator
        has_delete_perm = self.movement_list.has_delete_perm(creator)
        self.assertFalse(has_delete_perm)

    def test_movement_list_to_string_method(self):
        scheduled_datetime = datetime_to_current_tz(
            self.movement_list.scheduled_datetime
        ).strftime("%d.%m.%Y %H:%M")
        reference_string = "Заезд на " + scheduled_datetime
        string = str(self.movement_list)
        self.assertEqual(reference_string, string)


class MovementEntryModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        facility = FacilityObject.objects.create(
            name="Рудник Шануч",
            slug="shanuch-mine"
        )
        creator = get_user_model().objects.create_user(
            username="user1",
            email="user1@mail.com",
            password="user1pwd",
        )
        creator.first_name = "Александр"
        creator.last_name = "Бобров"
        creator.patronymic = "Сергеевич"
        creator.position = "Электрик"
        creator.save()
        movement_list = MovementList.objects.create(
            facility=facility,
            list_type=MovementList.ARRIVING,
            scheduled_datetime=timezone.now(),
            creator=creator,
        )
        employee = Employee.objects.create(
            first_name="Пётр",
            last_name="Орлов",
            patronymic="Ваганович",
            position="Водитель",
        )
        MovementEntry.objects.create(
            creator=creator,
            creation_datetime=timezone.now(),
            movement_list=movement_list,
            employee=employee,
        )

    def setUp(self):
        self.facility = FacilityObject.objects.get(slug="shanuch-mine")
        self.creator = get_user_model().objects.get(pk=1)
        self.movement_list = MovementList.objects.get(pk=1)
        self.movement_entry = self.movement_list.movemententry_set.get(pk=1)

    def test_get_url_kwargs_method(self):
        url_kwargs = self.movement_entry.get_url_kwargs()
        url_kwargs_keys = url_kwargs.keys()
        self.assertIsInstance(url_kwargs, dict)
        self.assertIn("facility_slug", list(url_kwargs_keys))
        self.assertIn("list_id", list(url_kwargs_keys))
        self.assertIn("entry_id", list(url_kwargs_keys))
        self.assertEqual(
            type(url_kwargs["facility_slug"]),
            str,
        )
        self.assertEqual(
            type(url_kwargs["list_id"]),
            int,
        )
        self.assertEqual(
            type(url_kwargs["entry_id"]),
            int,
        )
