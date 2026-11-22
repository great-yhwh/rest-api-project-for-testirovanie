import base64
import time
import requests
from django.conf import settings
from django.db.models import Avg
from .models import ExchangeLog


class IntegrationMonitoringService:
    ERROR_THRESHOLD_COUNT = 3

    @classmethod
    def _get_1c_auth_headers(cls) -> dict:
        """Формирование UTF-8 Basic Auth заголовка без зависимости от сервисов 1С."""
        auth_str = f"{settings.ODATA_USER}:{settings.ODATA_PASSWORD}"
        auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
        return {
            "Authorization": f"Basic {auth_b64}",
            "Accept": "application/json",
        }

    @classmethod
    def log_exchange(
            cls,
            operation: str,
            status_code: int,
            is_success: bool,
            response_time_ms: int,
            error_message: str = "",
            system_name: str = "1C:WarehouseSales",
    ) -> ExchangeLog:
        """Универсальный метод записи транзакций обмена в базу."""
        return ExchangeLog.objects.create(
            system_name=system_name,
            operation=operation,
            status_code=status_code,
            is_success=is_success,
            response_time_ms=response_time_ms,
            error_message=error_message,
        )

    @classmethod
    def check_1c_health(cls) -> dict:
        """Автономная проверка доступности OData 1С с поддержкой UTF-8 авторизации."""
        base_url = settings.ODATA_BASE_URL

        if not base_url.endswith("/"):
            base_url += "/"

        metadata_url = (
            f"{base_url}$metadata"
            if "standard.odata" in base_url
            else f"{base_url}odata/standard.odata/$metadata"
        )

        headers = cls._get_1c_auth_headers()
        start_time = time.time()

        try:
            response = requests.get(metadata_url, headers=headers, timeout=5)
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

    @classmethod
    def get_dashboard_metrics(cls) -> dict:
        """Расчет метрик обмена и агрегация данных для дашборда."""
        base_qs = ExchangeLog.objects.all()

        total_count = base_qs.count()
        failed_count = base_qs.filter(is_success=False).count()
        success_count = total_count - failed_count

        avg_latency = (
                base_qs.aggregate(avg_time=Avg("response_time_ms"))["avg_time"] or 0
        )

        recent_logs = list(base_qs[:10])
        recent_failures = sum(1 for log in recent_logs if not log.is_success)
        alert_triggered = recent_failures >= cls.ERROR_THRESHOLD_COUNT

        health_info = cls.check_1c_health()

        return {
            "logs": base_qs[:100],
            "total_count": total_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "avg_latency": round(avg_latency, 2),
            "recent_failures": recent_failures,
            "alert_triggered": alert_triggered,
            "error_threshold": cls.ERROR_THRESHOLD_COUNT,
            "health_info": health_info,
        }