from django.views.generic.list import ListView
from django.views.generic.base import RedirectView
from django.urls import reverse
from django.shortcuts import get_object_or_404, get_list_or_404

from movementcontrol.settings import DEBUG
from .models import FacilityObject, MovementEntry


class DefaultRedirect(RedirectView):
    """
    Редирект на страницу производственного объекта по умолчанию
    """

    permanent = False
    pattern_name = "main:facility-entries-list"


class FacilityMovementEntriesList(ListView):

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

    @property
    def related_facility(self):
        return get_object_or_404(
            FacilityObject, slug=self.kwargs["facility_slug"]
        )

    @property
    def all_facilities(self):
        return get_list_or_404(FacilityObject.objects.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["DEBUG"] = DEBUG
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["paginator"].baseurl = reverse(
            "main:facility-entries-list",
            args=[context["related_facility"].slug]
        ) + "?page="
        return context
