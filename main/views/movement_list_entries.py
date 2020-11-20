import pdfkit
import pytz

from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView, DeleteView
from django.template.loader import get_template
from django.views.decorators.http import require_safe
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q

from .mixins import FacilityListMixin
from ..models import FacilityObject, MovementList, Employee, MovementEntry,\
    MovementEntryHistory
from ..forms import CreateMovementEntryForm, EditMovementEntryForm,\
    SearchEntryForm
from ..utils import get_paginator_baseurl


class MovementListEntries(FacilityListMixin, ListView):

    template_name = "main/movement-list-entries/movement-list-entries.html"
    paginate_by = 10
    paginate_orphans = 0
    context_object_name = "entries"

    def get_queryset(self):
        entries = self.related_list.movemententry_set.all().order_by("-pk")
        search_request = self.request.GET.get("search_request", False)
        if search_request:
            search_request = search_request.strip().split()
            predicat = self.request.GET.get("predicat")
            for term in search_request:
                if predicat == "USERS":
                    entries = entries.filter(
                        Q(creator__first_name__icontains=term) |
                        Q(creator__last_name__icontains=term) |
                        Q(creator__patronymic__icontains=term)
                    )
                elif predicat == "EMPLOYEES":
                    entries = entries.filter(
                        Q(employee__first_name__icontains=term) |
                        Q(employee__last_name__icontains=term) |
                        Q(employee__patronymic__icontains=term)
                    )
        user = self.request.user
        out = []
        for entry in entries:
            change = entry.has_change_perm(user)
            delete = entry.has_delete_perm(user)
            out.append(
                {
                    "obj": entry,
                    "can_change": change,
                    "can_delete": delete,
                }
            )
        return out

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        context["paginator"].baseurl = get_paginator_baseurl(self.request)
        search_action = self.related_list.get_absolute_url()
        context["search_form"] = SearchEntryForm(search_action)
        return context


@require_safe
def movement_list_entries_PDF(request, **kwargs):

    related_facility = get_object_or_404(
        FacilityObject, slug=kwargs["facility_slug"]
    )
    related_list = get_object_or_404(
        MovementList, pk=kwargs["list_id"]
    )

    context = dict()
    context["header"] = related_facility.name
    context["related_facility"] = related_facility
    context["related_list"] = related_list
    context["entries"] = related_list.movemententry_set.all()

    template = get_template(
        "main/movement-list-entries/movement-list-entries-print.html"
    )
    html = template.render(context)
    pdf = pdfkit.from_string(html, False)
    settings_tz = pytz.timezone(settings.TIME_ZONE)
    scheduled_date = related_list.scheduled_datetime.astimezone(settings_tz)
    filename = context["related_facility"].slug + "-" +\
        scheduled_date.strftime("%d-%b-%Y") + ".pdf"

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="' + filename + '"'
    return response


class MovementListEntriesAdd(UserPassesTestMixin, FacilityListMixin, FormView):

    template_name = "main/movement-list-entries/movement-list-entries-add.html"
    form_class = CreateMovementEntryForm

    @property
    def success_url(self):
        context = self.get_context_data()
        return reverse(
            "movement-list-entries",
            args=[context["related_facility"].slug, self.kwargs["list_id"]]
        )

    def get_suggestions_dict(self):
        first_name_sug = MovementEntry.objects.get_autocomplete_suggestions("first_name")
        last_name_sug = MovementEntry.objects.get_autocomplete_suggestions("last_name")
        patronymic_sug = MovementEntry.objects.get_autocomplete_suggestions("patronymic")
        position_sug = MovementEntry.objects.get_autocomplete_suggestions("position")
        return {
            "first_name": first_name_sug,
            "last_name": last_name_sug,
            "patronymic": patronymic_sug,
            "position": position_sug,
        }

    def get_form_kwargs(self):
        kwargs = super(MovementListEntriesAdd, self).get_form_kwargs()
        kwargs["suggestions"] = self.get_suggestions_dict()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["related_list"] = self.related_list
        context["facilities"] = self.all_facilities
        return context

    def test_func(self):
        user = self.request.user
        return user.has_perm("main.add_movemententry")

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


class MovementListEntryEdit(UserPassesTestMixin, FacilityListMixin, UpdateView):

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

    def test_func(self):
        user = self.request.user
        cur_entry = self.get_object()
        print(cur_entry)
        can_change = cur_entry.has_change_perm(user)
        return can_change

    def form_valid(self, form):
        data = form.cleaned_data
        cur_employee = self.get_object().employee

        # Сериализируем данные до внесения изменения
        old_data = cur_employee.toJSON()

        # вносим изменения
        cur_employee.first_name = data["first_name"]
        cur_employee.last_name = data["last_name"]
        cur_employee.patronymic = data["patronymic"]
        cur_employee.position = data["position"]
        cur_employee.save()

        # Сериализируем данные после внесения изменения
        new_data = cur_employee.toJSON()

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


class MovementListEntryDelete(UserPassesTestMixin, FacilityListMixin, DeleteView):

    model = MovementEntry
    pk_url_kwarg = "entry_id"
    template_name = "main/movement-list-entries/movement-list-entries-delete.html"

    def get_success_url(self):
        return reverse("movement-list-entries", args=[
            self.related_facility.slug,
            self.related_list.pk,
        ])

    def get_object(self):
        return self.related_list.movemententry_set.get(
            pk=self.kwargs["entry_id"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        context["entry_id"] = self.kwargs["entry_id"]
        return context

    def test_func(self):
        user = self.request.user
        cur_entry = self.get_object()
        can_change = cur_entry.has_change_perm(user)
        return can_change

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Запись успешно удалена")
        return super().post(request, *args, **kwargs)


class MovementListEntryHistory(FacilityListMixin, ListView):

    template_name = "main/movement-list-entries/movement-list-entry-history.html"
    context_object_name = "history_entries"

    def get_queryset(self):
        entry = self.related_list.movemententry_set.get(
            pk=self.kwargs["entry_id"]
        )
        queryset = entry.movemententryhistory_set.all()
        queryset = queryset.order_by("-pk")
        data = []

        for obj in queryset:
            data.append(
                {
                    "meta": obj,
                    **obj.get_change_states(),
                }
            )

        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        return context
