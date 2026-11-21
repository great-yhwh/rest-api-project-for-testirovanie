import re
from django import forms


class ContractorForm(forms.Form):
    description = forms.CharField(
        label="Наименование контрагента",
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "ООО «Торговый Дом»"}
        ),
    )
    inn = forms.CharField(
        label="ИНН",
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    kpp = forms.CharField(
        label="КПП",
        max_length=9,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    legal_address = forms.CharField(
        label="Юридический адрес",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    contractor_type = forms.ChoiceField(
        label="Тип контрагента",
        choices=[("Покупатель", "Покупатель"), ("Поставщик", "Поставщик")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    phone = forms.CharField(
        label="Телефон",
        required=False,
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "phone-mask-input",
                "placeholder": "+7 (___) ___-__-__",
            }
        ),
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    def clean_inn(self):
        inn = self.cleaned_data.get("inn")
        if inn and not inn.isdigit():
            raise forms.ValidationError("ИНН должен состоять только из цифр!")
        return inn

    def clean_phone(self):
        """Очищает телефон от скобок, дефисов и пробелов: +7 (900) 000-00-00 -> +79000000000"""
        phone = self.cleaned_data.get("phone", "")
        if phone:
            # Оставляем только плюс и цифры
            phone = re.sub(r"[^\d+]", "", phone)
        return phone