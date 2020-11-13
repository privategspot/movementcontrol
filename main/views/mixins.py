from django.shortcuts import get_object_or_404, get_list_or_404

from ..models import FacilityObject, MovementList


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
