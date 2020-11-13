from django.contrib import messages
from django.core import serializers
from django.utils import timezone
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView, DeleteView

from .mixins import FacilityListMixin
from ..models import Employee, MovementEntry, MovementEntryHistory
from ..forms import CreateMovementEntryForm, EditMovementEntryForm


class MovementListEntries(FacilityListMixin, ListView):

    template_name = "main/movement-list-entries/movement-list-entries.html"
    ordering = ["-pk"]
    paginate_by = 10
    paginate_orphans = 0
    context_object_name = "entries"

    @property
    def queryset(self):
        return self.related_list.movemententry_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        context["paginator"].baseurl = reverse(
            "movement-list-entries",
            args=[
                context["related_facility"].slug,
                context["related_list"].pk,
            ]
        ) + "?page="
        return context


class MovementListEntriesAdd(FacilityListMixin, FormView):

    template_name = "main/movement-list-entries/movement-list-entries-add.html"
    form_class = CreateMovementEntryForm

    @property
    def success_url(self):
        context = self.get_context_data()
        return reverse(
            "movement-list-entries",
            args=[context["related_facility"].slug, self.kwargs["list_id"]]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["related_list"] = self.related_list
        context["facilities"] = self.all_facilities
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        employee = Employee.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            patronymic=data["patronymic"],
            position=data["position"]
        )
        MovementEntry.objects.create(
            movement_list=self.related_list,
            creator=self.request.user,
            employee=employee,
        )
        messages.success(self.request, "Запись успешно добавлена")
        return super().form_valid(form)


class MovementListEntryEdit(FacilityListMixin, UpdateView):

    form_class = EditMovementEntryForm
    template_name = "main/movement-list-entries/movement-list-entries-edit.html"
    pk_url_kwarg = "entry_id"

    @property
    def success_url(self):
        return reverse(
            "movement-list-entries",
            args=[
                self.kwargs["facility_slug"],
                self.kwargs["list_id"],
            ],
        )

    def get_object(self):
        return self.related_list.movemententry_set.get(
            pk=self.kwargs["entry_id"]
        )

    def get_queryset_with_object(self):
        return self.related_list.movemententry_set.filter(
            pk=self.kwargs["entry_id"]
        )

    def get_initial(self):
        obj = self.get_object()
        return {
            "first_name": obj.employee.first_name,
            "last_name": obj.employee.last_name,
            "patronymic": obj.employee.patronymic,
            "position": obj.employee.position,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        context["entry_id"] = self.kwargs["entry_id"]
        return context

    def form_valid(self, form):
        xml_serializer = serializers.get_serializer("xml")()
        data = form.cleaned_data
        queryset_with_cur_entry = self.get_queryset_with_object()

        # Сериализируем данные до внесения изменения
        old_data = xml_serializer.serialize(
            queryset_with_cur_entry,
            fields=("employee")
        )

        # вносим изменения
        cur_employee = queryset_with_cur_entry.get().employee
        cur_employee.first_name = data["first_name"]
        cur_employee.last_name = data["last_name"]
        cur_employee.patronymic = data["patronymic"]
        cur_employee.position = data["position"]
        cur_employee.save()

        # Сериализируем данные после внесения изменения
        new_data = xml_serializer.serialize(
            queryset_with_cur_entry,
            fields=("employee")
        )

        # добавляем запись в историю
        MovementEntryHistory.objects.create(
            modified_entry=self.get_object(),
            modified_by=self.request.user,
            modified_datetime=timezone.now(),
            serialized_prev_delta=old_data,
            serialized_post_delta=new_data,
        )

        messages.success(self.request, "Запись успешно изменена")
        return super().form_valid(form)


class MovementListEntryDelete(FacilityListMixin, DeleteView):

    model = MovementEntry
    pk_url_kwarg = "entry_id"
    template_name = "main/movement-list-entries/movement-list-entries-delete.html"

    def get_success_url(self):
        return reverse("movement-list-entries", args=[
            self.related_facility.slug,
            self.related_list.pk,
        ])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        context["entry_id"] = self.kwargs["entry_id"]
        return context

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Запись успешно удалена")
        return super().post(request, *args, **kwargs)


class MovementListEntryHistory(FacilityListMixin, ListView):
    pass
