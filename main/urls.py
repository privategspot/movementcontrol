from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required

from .views import DefaultRedirect, FacilityMovementEntriesList,\
    FacilityAddMovementEntry, FacilityMovementEntry


accounts_urls = [
    path(
        "accounts/login/",
        LoginView.as_view(redirect_authenticated_user=True),
        name="login"
    ),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
]

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
    path(
        "facility/<slug:facility_slug>/add/",
        login_required(FacilityAddMovementEntry.as_view()),
        name="facility-add-entry"
    ),
    path(
        "facility/<slug:facility_slug>/entry/<int:pk>/",
        FacilityMovementEntry.as_view(),
        name="movement-entry"
    )
] + accounts_urls
