from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required

from .views.base import DefaultRedirect
from .views.movement_lists import MovementLists, MovementListsAdd,\
    MovementListEdit, MovementListDelete, MovementListHistory
from .views.movement_list_entries import MovementListEntries,\
    MovementListEntriesAdd, MovementListEntryEdit, MovementListEntryDelete,\
    MovementListEntryHistory


accounts_urls = [
    path(
        "accounts/login/",
        LoginView.as_view(redirect_authenticated_user=True),
        name="login"
    ),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
]

movement_list_entries_urlpatterns = [
    path(
        "entries/",
        MovementListEntries.as_view(),
        name="movement-list-entries",
    ),
    path(
        "entries/add/",
        login_required(MovementListEntriesAdd.as_view()),
        name="movement-list-entries-add",
    ),
    path(
        "entries/<int:entry_id>/edit/",
        login_required(MovementListEntryEdit.as_view()),
        name="movement-list-entry-edit",
    ),
    path(
        "entries/<int:entry_id>/delete/",
        login_required(MovementListEntryDelete.as_view()),
        name="movement-list-entry-delete",
    ),
    path(
        "entries/<int:entry_id>/history/",
        MovementListEntryHistory.as_view(),
        name="movement-list-entry-history",
    ),
]

movement_lists_urlpatterns = [
    path(
        "lists/",
        MovementLists.as_view(),
        name="movement-lists",
    ),
    path(
        "lists/<int:list_id>/",
        include(movement_list_entries_urlpatterns),
    ),
    path(
        "lists/add/",
        login_required(MovementListsAdd.as_view()),
        name="movement-lists-add",
    ),
    path(
        "lists/<int:list_id>/edit/",
        login_required(MovementListEdit.as_view()),
        name="movement-list-edit",
    ),
    path(
        "lists/<int:list_id>/delete/",
        login_required(MovementListDelete.as_view()),
        name="movement-list-delete",
    ),
    path(
        "lists/<int:list_id>/history/",
        MovementListHistory.as_view(),
        name="movement-list-history",
    ),
]

urlpatterns = [
    path(
        "",
        DefaultRedirect.as_view(),
        {"facility_slug": "shanuch-mine"},
        name="redirect-to-default-facility",
    ),
    path(
        "facility/<slug:facility_slug>/",
        include(movement_lists_urlpatterns),
    ),
] + accounts_urls
