import base64
import json
from urllib.parse import quote

import requests
from django.conf import settings


class WarehouseSales1CService:
    """Интеграция с системой 'Управление складом и продажами' (1С OData)"""

    def __init__(self):
        self.base_url = settings.ODATA_BASE_URL

        auth_str = f"{settings.ODATA_USER}:{settings.ODATA_PASSWORD}"
        auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Accept": "application/json",
            "Content-Type": "application/json;odata=verbose;charset=utf-8",
        }

    def _url(self, endpoint: str) -> str:
        encoded_endpoint = quote(endpoint, safe="()'/=")
        return f"{self.base_url}{encoded_endpoint}"

    def _map_to_1c_contractor(self, data: dict) -> dict:
        """Универсальный маппинг: поддерживает и латинские, и кириллические ключи формы"""
        return {
            "Description": str(
                data.get("description") or data.get("Description") or ""
            ),
            "ИНН": str(data.get("inn") or data.get("ИНН") or ""),
            "КПП": str(data.get("kpp") or data.get("КПП") or ""),
            "ЮридическийАдрес": str(
                data.get("legal_address") or data.get("ЮридическийАдрес") or ""
            ),
            "ТипКонтрагента": str(
                data.get("contractor_type")
                or data.get("ТипКонтрагента")
                or "Покупатель"
            ),
            "Телефон": str(data.get("phone") or data.get("Телефон") or ""),
            "email": str(data.get("email") or ""),
        }

    def _map_from_1c_contractor(self, odata_dict: dict) -> dict:
        return {
            "description": odata_dict.get("Description"),
            "inn": odata_dict.get("ИНН"),
            "kpp": odata_dict.get("КПП"),
            "legal_address": odata_dict.get("ЮридическийАдрес"),
            "contractor_type": odata_dict.get("ТипКонтрагента"),
            "phone": odata_dict.get("Телефон"),
            "email": odata_dict.get("email"),
        }

    # --- GUID -> Название ---
    def get_warehouses_map(self) -> dict:
        url = self._url("Catalog_Склады")
        try:
            res = requests.get(url, headers=self.headers, timeout=5)
            if res.status_code == 200:
                return {
                    item["Ref_Key"]: item.get("Description", "Без названия")
                    for item in res.json().get("value", [])
                }
        except Exception:
            pass
        return {}

    def get_nomenclature_map(self) -> dict:
        url = self._url("Catalog_Номенклатура")
        try:
            res = requests.get(url, headers=self.headers, timeout=5)
            if res.status_code == 200:
                return {
                    item["Ref_Key"]: item.get("Description", "Без названия")
                    for item in res.json().get("value", [])
                }
        except Exception:
            pass
        return {}

    # --- CRUD Методы ---
    def get_contractors(self):
        url = self._url("Catalog_Контрагенты")
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                return response.json().get("value", [])
        except Exception:
            pass
        return []

    def get_contractor(self, ref_key: str):
        url = self._url(f"Catalog_Контрагенты(guid'{ref_key}')")
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_contractor_for_form(self, ref_key: str):
        contractor = self.get_contractor(ref_key)
        if contractor:
            return self._map_from_1c_contractor(contractor)
        return None

    def create_contractor(self, form_data: dict):
        url = self._url("Catalog_Контрагенты")
        payload = self._map_to_1c_contractor(form_data)
        json_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        try:
            response = requests.post(
                url, headers=self.headers, data=json_bytes, timeout=5
            )
            if response.status_code in (200, 201):
                return True, response.json()

            err_msg = (
                f"Код {response.status_code}: Не удалось сохранить запись в 1С."
            )
            if "application/json" in response.headers.get("Content-Type", ""):
                err_msg = response.json()
            return False, err_msg
        except Exception as e:
            return False, f"Ошибка сети при обращении к 1С: {e}"

    def update_contractor(self, ref_key: str, form_data: dict) -> bool:
        url = self._url(f"Catalog_Контрагенты(guid'{ref_key}')")
        payload = self._map_to_1c_contractor(form_data)
        json_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        response = requests.patch(url, headers=self.headers, data=json_bytes)
        return response.status_code in (200, 204)

    def delete_contractor(self, ref_key: str) -> bool:
        url = self._url(f"Catalog_Контрагенты(guid'{ref_key}')")
        response = requests.delete(url, headers=self.headers)
        return response.status_code in (200, 204)

    def get_stock_balances(self):
        url = self._url("AccumulationRegister_ОстаткиТоваров/Balance")
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code != 200:
                return []

            balances = response.json().get("value", [])
            if not balances:
                return []

            warehouses_map = self.get_warehouses_map()
            nomenclature_map = self.get_nomenclature_map()

            enriched_balances = []
            for item in balances:
                sklad_guid = item.get("Склад_Key")
                nom_guid = item.get("Номенклатура_Key")

                enriched_balances.append(
                    {
                        "sklad_name": warehouses_map.get(
                            sklad_guid, sklad_guid or "Не указан"
                        ),
                        "nomenclature_name": nomenclature_map.get(
                            nom_guid, nom_guid or "Не указана"
                        ),
                        "balance": item.get("КоличествоBalance", 0),
                    }
                )

            return enriched_balances
        except Exception:
            return []