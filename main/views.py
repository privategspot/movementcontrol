from django.views.generic.list import ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView
from django.urls import reverse
from django.shortcuts import get_object_or_404, get_list_or_404

from movementcontrol.settings import DEBUG
from .models import FacilityObject, MovementEntry
from .forms import CreateMovementEntryForm


class FacilityMixin:

    @property
    def related_facility(self):
        return get_object_or_404(
            FacilityObject, slug=self.kwargs["facility_slug"]
        )

    @property
    def all_facilities(self):
        return get_list_or_404(FacilityObject.objects.all())


class DefaultRedirect(RedirectView):
    """
    Редирект на страницу производственного объекта по умолчанию
    """

    permanent = False
    pattern_name = "facility-entries-list"


class FacilityMovementEntriesList(FacilityMixin, ListView):

    template_name = "main/entries-list.html"
    ordering = ["-pk"]
    paginate_by = 48
    paginate_orphans = 0
    context_object_name = "entries"

    @property
    def queryset(self):
        return MovementEntry.objects.filter(
            facility__slug=self.kwargs["facility_slug"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DEBUG"] = DEBUG
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["paginator"].baseurl = reverse(
            "facility-entries-list",
            args=[context["related_facility"].slug]
        ) + "?page="
        return context


class FacilityAddMovementEntry(FacilityMixin, FormView):

    template_name = "main/add-entry.html"
    form_class = CreateMovementEntryForm

    @property
    def success_url(self):
        return reverse(
            "facility-entries-list",
            args=[self.get_context_data()["related_facility"].slug]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DEBUG"] = DEBUG
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        return context
