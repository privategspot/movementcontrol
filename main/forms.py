from django import forms
from django.utils import timezone

from .models import MovementList, Employee


class CreateMovementListForm(forms.ModelForm):

    class Meta:
        model = MovementList
        fields = ["list_type", "scheduled_datetime"]
        labels = {
            "scheduled_datetime": "Дата заезда/отъезда"
        }
        widgets = {
            "scheduled_datetime": forms.DateTimeInput(
                attrs={
                    "placeholder": "25.10.2020 14:30",
                    "type": "date",
                    "min": timezone.now().strftime("%Y-%m-%d")
                }
            )
        }


class EditMovementListForm(forms.ModelForm):

    class Meta:
        model = MovementList
        fields = ["scheduled_datetime"]
        labels = {
            "scheduled_datetime": "Дата заезда/отъезда"
        }
        widgets = {
            "scheduled_datetime": forms.DateTimeInput(
                attrs={
                    "placeholder": "25.10.2020 14:30",
                    "type": "date",
                    "min": timezone.now().strftime("%Y-%m-%d")
                }
            )
        }


class CreateMovementEntryForm(forms.Form):
    first_name = forms.CharField(
        min_length=2,
        max_length=40,
        label="Имя сотрудника",
        widget=forms.TextInput(attrs={"placeholder": "Иван"})
    )
    last_name = forms.CharField(
        min_length=2,
        max_length=40,
        label="Фамилия сотрудника",
        widget=forms.TextInput(attrs={"placeholder": "Иванов"})
    )
    patronymic = forms.CharField(
        min_length=2,
        max_length=40,
        label="Отчество сотрудника",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Иванович"})
    )
    position = forms.CharField(
        min_length=0,
        max_length=100,
        label="Должность",
    )

    field_order = [
        "first_name",
        "last_name",
        "patronymic",
        "position",
    ]


class EditMovementEntryForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = "__all__"
