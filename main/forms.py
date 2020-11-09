from django import forms


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
