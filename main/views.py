from django.views.generic.list import ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse
from django.utils import timezone
from django.core import serializers
from django.shortcuts import get_object_or_404, get_list_or_404

from movementcontrol.settings import DEBUG
from .models import FacilityObject, MovementEntry, Employee, MovementList,\
    MovementListHistory
from .forms import CreateMovementEntryForm, CreateMovementListForm,\
    EditMovementListForm


class FacilityMixin:

    @property
    def related_facility(self):
        return get_object_or_404(
            FacilityObject, slug=self.kwargs["facility_slug"]
        )

    @property
    def all_facilities(self):
        return get_list_or_404(FacilityObject.objects.all())


class FacilityListMixin(FacilityMixin):

    @property
    def related_list(self):
        return get_object_or_404(
            MovementList, pk=self.kwargs["list_id"]
        )


class DefaultRedirect(RedirectView):
    """
    Редирект на страницу производственного объекта по умолчанию
    """

    permanent = False
    pattern_name = "facility-lists"


class FacilityLists(FacilityMixin, ListView):

    template_name = "main/facility-lists.html"
    ordering = ["-pk"]
    paginate_by = 48
    paginate_orphans = 0
    context_object_name = "movement_lists"

    @property
    def queryset(self):
        return self.related_facility.movementlist_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DEBUG"] = DEBUG
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["paginator"].baseurl = reverse(
            "facility-lists",
            args=[context["related_facility"].slug]
        ) + "?page="
        return context


class AddMovementList(FacilityMixin, FormView):

    template_name = "main/add-list.html"
    form_class = CreateMovementListForm

    @property
    def success_url(self):
        return reverse(
            "facility-lists",
            args=[self.get_context_data()["related_facility"].slug]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DEBUG"] = DEBUG
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        MovementList.objects.create(
            facility=self.related_facility,
            list_type=data["list_type"],
            scheduled_datetime=data["scheduled_datetime"],
            creator=self.request.user,
        )
        return super().form_valid(form)


class DeleteMovementList(FacilityListMixin, DeleteView):

    model = MovementList
    template_name = "main/facility-list-delete-confirm.html"
    pk_url_kwarg = "list_id"

    def get_success_url(self):
        return reverse('facility-lists', args=[self.related_facility.slug])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DEBUG"] = DEBUG
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        return context


class EditMovementList(FacilityListMixin, UpdateView):

    form_class = EditMovementListForm
    template_name = "main/edit-list.html"
    pk_url_kwarg = "list_id"

    @property
    def success_url(self):
        return reverse(
            "facility-lists",
            args=[self.kwargs["facility_slug"]]
        )

    def get_object(self):
        return self.related_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DEBUG"] = DEBUG
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        cur_list = self.related_list
        MovementListHistory.objects.create(
            modified_list=cur_list,
            modified_by=self.request.user,
            modified_datetime=timezone.now(),
            serialized_model_delta=serializers.serialize(
                "xml",
                self.related_facility.movementlist_set.filter(
                    pk=self.kwargs["list_id"]
                ),
                fields=("scheduled_datetime")
            )
        )
        cur_list.scheduled_datetime = data["scheduled_datetime"]
        return super().form_valid(form)


class MovementListHistoryView(FacilityListMixin, ListView):

    template_name = "main/facility-list-history.html"
    context_object_name = "history_entries"

    def get_queryset(self):
        queryset = self.related_list.movementlisthistory_set.all()
        queryset = queryset.order_by("-pk")
        data = []

        for obj in queryset:
            deserialized_data = []
            for deserialized_object in serializers.deserialize(
                "xml", obj.serialized_model_delta
            ):
                deserialized_data.append(deserialized_object.object)

            data.append(
                {"obj": obj, "deserialized_data": deserialized_data[0]}
            )

        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DEBUG"] = DEBUG
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        return context


class FacilityMovementEntriesList(FacilityListMixin, ListView):

    template_name = "main/entries-list.html"
    ordering = ["-pk"]
    paginate_by = 48
    paginate_orphans = 0
    context_object_name = "entries"

    @property
    def queryset(self):
        return self.related_list.movemententry_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DEBUG"] = DEBUG
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        context["paginator"].baseurl = reverse(
            "facility-entries-list",
            args=[
                context["related_facility"].slug,
                context["related_list"].pk,
            ]
        ) + "?page="
        return context


class FacilityAddMovementEntry(FacilityListMixin, FormView):

    template_name = "main/add-entry.html"
    form_class = CreateMovementEntryForm

    @property
    def success_url(self):
        context = self.get_context_data()
        return reverse(
            "facility-entries-list",
            args=[context["related_facility"].slug, self.kwargs["list_id"]]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DEBUG"] = DEBUG
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
        return super().form_valid(form)


class FacilityMovementEntry(FacilityListMixin, DetailView):

    template_name = "main/entry-detail.html"
    context_object_name = "entry"
    model = MovementEntry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DEBUG"] = DEBUG
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["related_list"] = self.related_list
        context["facilities"] = self.all_facilities
        return context
