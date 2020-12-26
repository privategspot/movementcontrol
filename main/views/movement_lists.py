import datetime

from django.contrib import messages
from django.urls import reverse
from django.core import serializers
from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect

from .mixins import FacilityMixin, FacilityListMixin
from ..models import MovementList,\
    MovementListHistory as MovementListHistoryModel
from ..forms import CreateMovementListForm, EditMovementListForm,\
    SearchListForm
from ..utils import get_paginator_baseurl, datetime_to_current_tz
from ..utils.link import Link


class MovementLists(FacilityMixin, ListView):

    template_name = "main/movement-lists/movement-lists.html"
    paginate_by = 10
    paginate_orphans = 0
    context_object_name = "movement_lists"
    http_method_names = ["get", "head"]

    def get_queryset(self):
        get_params = self.request.GET
        movement_lists =\
            self.related_facility.movementlist_set.all().order_by("-pk")
        show = get_params.get("show", "")
        if show == "arrivals":
            movement_lists = movement_lists.filter(list_type="ARR")
        elif show == "departures":
            movement_lists = movement_lists.filter(list_type="LVN")

        search_date = get_params.get("search_date", False)
        if search_date:
            print("request")
            movement_lists = movement_lists.filter(
                scheduled_datetime__contains=search_date
            )

        user = self.request.user
        out = []
        for mlist in movement_lists:
            change = mlist.has_change_perm(user) and not mlist.is_deleted
            delete = mlist.has_delete_perm(user) and not mlist.is_deleted
            out.append(
                {
                    "obj": mlist,
                    "can_change": change,
                    "can_delete": delete,
                }
            )
        return out

    def get_show_message(self):
        cur_get = self.request.GET
        if "show" not in cur_get:
            return "все"
        elif cur_get["show"] == "arrivals":
            return "только заезды"
        elif cur_get["show"] == "departures":
            return "только выезды"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["paginator"].baseurl = get_paginator_baseurl(self.request)
        context["show"] = self.get_show_message()
        search_action = self.related_facility.get_absolute_url()
        context["search_form"] = SearchListForm(search_action)
        return context


class MovementListsAdd(UserPassesTestMixin, FacilityMixin, FormView):

    template_name = "main/movement-lists/movement-lists-add.html"
    form_class = CreateMovementListForm

    @property
    def success_url(self):
        return reverse(
            "movement-lists",
            args=[self.get_context_data()["related_facility"].slug]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        return context

    def test_func(self):
        user = self.request.user
        return user.has_perm("main.add_movementlist")

    def get_form_kwargs(self):
        kwargs = super(MovementListsAdd, self).get_form_kwargs()
        kwargs["perms"] = self.request.user.get_all_permissions()
        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data
        MovementList.objects.create(
            facility=self.related_facility,
            list_type=data["list_type"],
            scheduled_datetime=datetime.datetime.combine(
                data["move_date"],
                data["move_time"],
            ),
            creator=self.request.user,
            watch=data["watch"],
            place=data["place"],
        )
        messages.success(self.request, "Список успешно добавлен")
        return super().form_valid(form)


class MovementListEdit(UserPassesTestMixin, FacilityListMixin, FormView):

    form_class = EditMovementListForm
    template_name = "main/movement-lists/movement-list-edit.html"
    pk_url_kwarg = "list_id"

    @property
    def success_url(self):
        return reverse(
            "movement-lists",
            args=[self.kwargs["facility_slug"]]
        )

    def get_object(self):
        return self.related_list

    def test_func(self):
        user = self.request.user
        cur_list = self.get_object()
        can_change = cur_list.has_change_perm(user) and not cur_list.is_deleted
        return can_change

    def get_breadcrumbs_links(self):
        return [
            Link(
                self.related_facility.get_absolute_url(),
                self.related_facility,
            ),
            Link(
                self.related_list.get_absolute_url(),
                self.related_list,
            ),
            Link(
                self.related_list.get_edit_url(),
                "Перенос даты",
            ),
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        context["links"] = self.get_breadcrumbs_links()
        return context

    def get_initial(self):
        list_datetime = datetime_to_current_tz(
            self.related_list.scheduled_datetime
        )
        return {
            "move_date": list_datetime.date,
            "move_time": list_datetime.time().strftime("%H:%M"),
            "place": self.related_list.place,
        }

    def get_form_kwargs(self):
        kwargs = super(MovementListEdit, self).get_form_kwargs()
        kwargs["perms"] = self.request.user.get_all_permissions()
        return kwargs

    def form_valid(self, form):
        xml_serializer = serializers.get_serializer("xml")()
        data = form.cleaned_data
        cur_list = self.get_object()

        # Сериализируем данные до внесения изменения
        old_data = xml_serializer.serialize(
            [cur_list],
            fields=("scheduled_datetime")
        )

        # вносим изменения
        new_scheduled_datetime = datetime.datetime.combine(
            data["move_date"],
            data["move_time"],
        )
        cur_list.scheduled_datetime = new_scheduled_datetime
        cur_list.was_modified = True
        cur_list.watch = data["watch"]
        cur_list.place = data["place"]
        cur_list.save()

        # Сериализируем данные после внесения изменения
        new_data = xml_serializer.serialize(
            [cur_list],
            fields=("scheduled_datetime")
        )

        # добавляем запись в историю
        MovementListHistoryModel.objects.create(
            modified_list=cur_list,
            modified_by=self.request.user,
            modified_datetime=timezone.now(),
            serialized_prev_delta=old_data,
            serialized_post_delta=new_data,
        )

        messages.success(self.request, "Список успешно изменён")
        return super().form_valid(form)


class MovementListDelete(UserPassesTestMixin, FacilityListMixin, DeleteView):

    model = MovementList
    template_name = "main/movement-lists/movement-list-delete.html"
    pk_url_kwarg = "list_id"

    def get_success_url(self):
        return reverse('movement-lists', args=[self.related_facility.slug])

    def get_object(self):
        return self.related_list

    def test_func(self):
        user = self.request.user
        cur_list = self.get_object()
        can_delete = cur_list.has_delete_perm(user) and not cur_list.is_deleted
        return can_delete

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        return context

    def delete(self):
        obj = self.get_object()
        obj.is_deleted = True
        obj.save()
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Список помечен как удаленный")
        return self.delete()


class MovementListHistory(FacilityListMixin, ListView):

    template_name = "main/movement-lists/movement-list-history.html"
    context_object_name = "history_entries"

    def get_queryset(self):
        queryset = self.related_list.movementlisthistory_set.all()
        queryset = queryset.order_by("-pk")
        data = []

        for obj in queryset:
            deserialized_data = []
            for deserialized_object in serializers.deserialize(
                "xml",
                obj.serialized_prev_delta
            ):
                deserialized_data.append(deserialized_object.object)

            for deserialized_object in serializers.deserialize(
                "xml",
                obj.serialized_post_delta
            ):
                deserialized_data.append(deserialized_object.object)

            data.append(
                {
                    "entry": obj,
                    "prev_change": deserialized_data[0],
                    "post_change": deserialized_data[1],
                }
            )

        return data

    def get_breadcrumbs_links(self):
        return [
            Link(
                self.related_facility.get_absolute_url(),
                self.related_facility,
            ),
            Link(
                self.related_list.get_absolute_url(),
                self.related_list,
            ),
            Link(
                self.related_list.get_history_url(),
                "История изменений",
            ),
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        context["links"] = self.get_breadcrumbs_links()
        return context
