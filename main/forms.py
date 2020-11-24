from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import MovementList, Employee, MovementEntry
from .widgets import ListTextWidget


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = UserCreationForm._meta.fields +\
            ("first_name", "last_name", "patronymic", "position")


class CustomUserChangeForm(UserChangeForm):
    pass


class CreateMovementListForm(forms.ModelForm):

    move_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "placeholder": "25.10.2020",
                "type": "date",
                "min": timezone.now().strftime("%Y-%m-%d")
            }
        ),
        label="Дата"
    )
    move_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                "placeholder": "14:30",
                "type": "time",
            }
        ),
        label="Время"
    )

    class Meta:
        model = MovementList
        fields = ["list_type"]


class EditMovementListForm(forms.ModelForm):

    class Meta:
        model = MovementList
        fields = ["scheduled_datetime"]
        labels = {
            "scheduled_datetime": "Дата заезда/выезда"
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
    )
    last_name = forms.CharField(
        min_length=2,
        max_length=40,
        label="Фамилия сотрудника",
    )
    patronymic = forms.CharField(
        min_length=2,
        max_length=40,
        label="Отчество сотрудника",
        required=False,
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

    def __init__(self, *args, **kwargs):
        _suggestions = kwargs.pop("suggestions", None)
        super(CreateMovementEntryForm, self).__init__(*args, **kwargs)

        self.fields["first_name"].widget = ListTextWidget(
            attrs={"placeholder": "Иван", "autocomplete": "off"},
            data_list=_suggestions.get("first_name", []),
            name="first_name_sug"
        )
        self.fields["last_name"].widget = ListTextWidget(
            attrs={"placeholder": "Иванов", "autocomplete": "off"},
            data_list=_suggestions.get("last_name", []),
            name="last_name_sug"
        )
        self.fields["patronymic"].widget = ListTextWidget(
            attrs={"placeholder": "Иванович", "autocomplete": "off"},
            data_list=_suggestions.get("patronymic", []),
            name="patronymic_sug"
        )
        self.fields["position"].widget = ListTextWidget(
            attrs={"autocomplete": "off"},
            data_list=_suggestions.get("position", []),
            name="position_sug",
        )


class EditMovementEntryForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = "__all__"


class SearchEntryForm(forms.Form):

    def __init__(self, action, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.disable_csrf = True
        self.helper.form_method = "GET"
        self.helper.form_action = action
        self.helper.add_input(Submit("submit", "Найти"))

    PREDICATS = [
        ("EMPLOYEES", "ФИО сотрудника"),
        ("USERS", "ФИО автора"),
    ]

    search_request = forms.CharField(label="Запрос")
    predicat = forms.ChoiceField(
        label="Искать по",
        widget=forms.Select(),
        choices=PREDICATS,
    )
