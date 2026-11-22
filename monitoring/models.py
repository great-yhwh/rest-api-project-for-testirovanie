from django.db import models

class ExchangeLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время операции")
    system_name = models.CharField(
        max_length=100,
        default="1C:WarehouseSales",
        verbose_name="Внешняя система / Модуль"
    )
    operation = models.CharField(max_length=255, verbose_name="Операция / Эндпоинт")
    status_code = models.IntegerField(verbose_name="HTTP Код")
    is_success = models.BooleanField(default=True, verbose_name="Успешно")
    response_time_ms = models.IntegerField(verbose_name="Время отклика (мс)")
    error_message = models.TextField(blank=True, null=True, verbose_name="Детали ошибки / Payload")

    class Meta:
        verbose_name = "Журнал обмена"
        verbose_name_plural = "Журнал обменов"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.system_name} - {self.operation} ({self.status_code})"