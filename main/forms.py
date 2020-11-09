from django import forms
from django.utils import timezone

from .models import MovementEntry


class CreateMovementEntryForm(forms.ModelForm):
    first_name = forms.CharField(
        min_length=2,
        max_length=40,
        label="Имя сотрудника",
        widget=forms.TextInput(attrs={"placeholder": "Иван"})
    )
    second_name = forms.CharField(
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
        "second_name",
        "patronymic",
        "position",
        "list_type",
        "scheduled_datetime",
    ]

    class Meta:
        model = MovementEntry
        fields = ["entry_type", "scheduled_datetime"]
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
