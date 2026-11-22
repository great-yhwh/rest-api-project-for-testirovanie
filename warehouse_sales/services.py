import base64
import json
import time
from urllib.parse import quote

import requests
from django.conf import settings
from monitoring.services import IntegrationMonitoringService


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

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Единый метод отправки запросов в 1С с записью логов в модуль мониторинга."""
        url = self._url(endpoint)
        start_time = time.time()

        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)

            is_success = response.status_code in (200, 201, 204)
            error_msg = "" if is_success else response.text[:500]

            IntegrationMonitoringService.log_exchange(
                system_name="1C:WarehouseSales",
                operation=f"{method} {endpoint.split('?')[0]}",
                status_code=response.status_code,
                is_success=is_success,
                response_time_ms=duration_ms,
                error_message=error_msg,
            )
            return response

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            IntegrationMonitoringService.log_exchange(
                system_name="1C:WarehouseSales",
                operation=f"{method} {endpoint.split('?')[0]}",
                status_code=500,
                is_success=False,
                response_time_ms=duration_ms,
                error_message=str(e),
            )
            raise

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
        try:
            res = self._make_request("GET", "Catalog_Склады", timeout=5)
            if res.status_code == 200:
                return {
                    item["Ref_Key"]: item.get("Description", "Без названия")
                    for item in res.json().get("value", [])
                }
        except Exception:
            pass
        return {}

    def get_nomenclature_map(self) -> dict:
        try:
            res = self._make_request("GET", "Catalog_Номенклатура", timeout=5)
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
        try:
            response = self._make_request("GET", "Catalog_Контрагенты", timeout=5)
            if response.status_code == 200:
                return response.json().get("value", [])
        except Exception:
            pass
        return []

    def get_contractor(self, ref_key: str):
        response = self._make_request("GET", f"Catalog_Контрагенты(guid'{ref_key}')")
        if response.status_code == 200:
            return response.json()
        return None

    def get_contractor_for_form(self, ref_key: str):
        contractor = self.get_contractor(ref_key)
        if contractor:
            return self._map_from_1c_contractor(contractor)
        return None

    def create_contractor(self, form_data: dict):
        payload = self._map_to_1c_contractor(form_data)
        json_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        try:
            response = self._make_request(
                "POST", "Catalog_Контрагенты", data=json_bytes, timeout=5
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
        payload = self._map_to_1c_contractor(form_data)
        json_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        response = self._make_request(
            "PATCH", f"Catalog_Контрагенты(guid'{ref_key}')", data=json_bytes
        )
        return response.status_code in (200, 204)

    def delete_contractor(self, ref_key: str) -> bool:
        response = self._make_request(
            "DELETE", f"Catalog_Контрагенты(guid'{ref_key}')"
        )
        return response.status_code in (200, 204)

    def get_stock_balances(self):
        """Получение остатков товаров с разрешением GUID складов и номенклатуры."""
        try:
            response = self._make_request(
                "GET", "AccumulationRegister_ОстаткиТоваров/Balance", timeout=5
            )
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

    def check_health(self) -> dict:
        """Проверка доступности OData-эндпоинта 1С с использованием корректной UTF-8 авторизации."""
        metadata_url = f"{self.base_url}$metadata"
        start_time = time.time()

        try:
            response = requests.get(
                metadata_url, headers=self.headers, timeout=5
            )
            latency_ms = int((time.time() - start_time) * 1000)
            is_healthy = response.status_code == 200
            status_text = (
                "OK (200)" if is_healthy else f"Error ({response.status_code})"
            )
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            is_healthy = False
            status_text = f"Unreachable: {str(e)}"

        return {
            "is_healthy": is_healthy,
            "status_text": status_text,
            "latency_ms": latency_ms,
            "url": metadata_url,
        }