from django.contrib import messages
from django.urls import reverse
from django.core import serializers
from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView, DeleteView

from .mixins import FacilityMixin, FacilityListMixin
from ..models import MovementList,\
    MovementListHistory as MovementListHistoryModel
from ..forms import CreateMovementListForm, EditMovementListForm


class MovementLists(FacilityMixin, ListView):

    template_name = "main/movement-lists/movement-lists.html"
    ordering = ["-pk"]
    paginate_by = 10
    paginate_orphans = 0
    context_object_name = "movement_lists"

    @property
    def queryset(self):
        return self.related_facility.movementlist_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["paginator"].baseurl = reverse(
            "movement-lists",
            args=[context["related_facility"].slug]
        ) + "?page="
        return context


class MovementListsAdd(FacilityMixin, FormView):

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

    def form_valid(self, form):
        data = form.cleaned_data
        MovementList.objects.create(
            facility=self.related_facility,
            list_type=data["list_type"],
            scheduled_datetime=data["scheduled_datetime"],
            creator=self.request.user,
        )
        messages.success(self.request, "Список успешно добавлен")
        return super().form_valid(form)


class MovementListEdit(FacilityListMixin, UpdateView):

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        return context

    def form_valid(self, form):
        xml_serializer = serializers.get_serializer("xml")()
        data = form.cleaned_data
        cur_list = self.related_list
        queryset_with_cur_list = self.related_facility.movementlist_set.filter(
            pk=self.kwargs["list_id"]
        )

        # Сериализируем данные до внесения изменения
        old_data = xml_serializer.serialize(
            queryset_with_cur_list,
            fields=("scheduled_datetime")
        )

        # вносим изменения
        queryset_with_cur_list[0].scheduled_datetime = data["scheduled_datetime"]
        queryset_with_cur_list[0].save(update_fields=["scheduled_datetime"])

        # Сериализируем данные после внесения изменения
        new_data = xml_serializer.serialize(
            queryset_with_cur_list,
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


class MovementListDelete(FacilityListMixin, DeleteView):

    model = MovementList
    template_name = "main/movement-lists/movement-list-delete.html"
    pk_url_kwarg = "list_id"

    def get_success_url(self):
        return reverse('movement-lists', args=[self.related_facility.slug])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        return context

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Список успешно удалён")
        return super().post(request, *args, **kwargs)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["header"] = self.related_facility.name
        context["related_facility"] = self.related_facility
        context["facilities"] = self.all_facilities
        context["related_list"] = self.related_list
        return context
