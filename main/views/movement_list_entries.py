from django.contrib import messages
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView, DeleteView

from .mixins import FacilityListMixin
from ..models import Employee, MovementEntry
from ..forms import CreateMovementEntryForm


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
    pass


class MovementListEntryDelete(FacilityListMixin, DeleteView):
    pass


class MovementListEntryHistory(FacilityListMixin, ListView):
    pass
