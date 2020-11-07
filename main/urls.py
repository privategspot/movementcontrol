from django.urls import path

from .views import DefaultRedirect, FacilityMovementEntriesList


app_name = "main"
urlpatterns = [
    path(
        "",
        DefaultRedirect.as_view(),
        {"facility_slug": "shanuch-mine"},
        name="redirect-to-default-facility-list",
    ),
    path(
        "facility/<slug:facility_slug>/",
        FacilityMovementEntriesList.as_view(),
        name="facility-entries-list"
    ),
]
