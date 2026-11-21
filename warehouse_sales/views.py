from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContractorForm
from .services import WarehouseSales1CService

service_1c = WarehouseSales1CService()


def _map_form_to_odata(cleaned_data: dict) -> dict:
    """Преобразует данные из формы Django (латиница) в формат 1С OData (кириллица)."""
    return {
        "Description": cleaned_data.get("description"),
        "ИНН": cleaned_data.get("inn"),
        "КПП": cleaned_data.get("kpp"),
        "ЮридическийАдрес": cleaned_data.get("legal_address"),
        "ТипКонтрагента": cleaned_data.get("contractor_type"),
        "Телефон": cleaned_data.get("phone"),
        "email": cleaned_data.get("email"),
    }


def _map_odata_to_form(contractor_odata: dict) -> dict:
    """Преобразует данные из 1С OData (кириллица) в начальные данные формы Django (латиница)."""
    return {
        "description": contractor_odata.get("Description"),
        "inn": contractor_odata.get("ИНН"),
        "kpp": contractor_odata.get("КПП"),
        "legal_address": contractor_odata.get("ЮридическийАдрес"),
        "contractor_type": contractor_odata.get("ТипКонтрагента"),
        "phone": contractor_odata.get("Телефон"),
        "email": contractor_odata.get("email"),
    }


def contractor_list(request):
    contractors = service_1c.get_contractors()
    return render(
        request, 'contractor_list.html', {'contractors': contractors}
    )


def contractor_create(request):
    if request.method == 'POST':
        form = ContractorForm(request.POST)
        if form.is_valid():
            odata_payload = _map_form_to_odata(form.cleaned_data)
            success, result = service_1c.create_contractor(odata_payload)
            if success:
                messages.success(request, "Контрагент успешно сохранен!")
                return redirect('warehouse_sales:contractor_list')
            else:
                messages.error(request, f"Ошибка: {result}")
    else:
        form = ContractorForm()

    return render(
        request,
        'contractor_form.html',
        {'form': form, 'title': 'Добавить контрагента'},
    )


def contractor_update(request, ref_key):
    contractor = service_1c.get_contractor(ref_key)
    if not contractor:
        messages.error(request, "Запись не найдена!")
        return redirect('warehouse_sales:contractor_list')

    if request.method == 'POST':
        form = ContractorForm(request.POST)
        if form.is_valid():
            odata_payload = _map_form_to_odata(form.cleaned_data)
            if service_1c.update_contractor(ref_key, odata_payload):
                messages.success(request, "Данные успешно обновлены!")
                return redirect('warehouse_sales:contractor_list')
            else:
                messages.error(request, "Не удалось обновить запись")
    else:
        initial_data = _map_odata_to_form(contractor)
        form = ContractorForm(initial=initial_data)

    return render(
        request,
        'contractor_form.html',
        {'form': form, 'title': 'Изменить данные контрагента'},
    )


def contractor_delete(request, ref_key):
    if service_1c.delete_contractor(ref_key):
        messages.success(request, "Контрагент удален!")
    else:
        messages.error(request, "Ошибка при удалении записи")
    return redirect('warehouse_sales:contractor_list')


def stock_list(request):
    balances = service_1c.get_stock_balances()
    return render(request, 'stock_list.html', {'balances': balances})