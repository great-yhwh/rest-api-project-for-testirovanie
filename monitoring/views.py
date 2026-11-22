from django.shortcuts import render
from .services import IntegrationMonitoringService


def monitoring_dashboard(request):
    """Отображение единой консоли мониторинга интеграций."""
    context = IntegrationMonitoringService.get_dashboard_metrics()
    return render(request, "monitoring.html", context)