from django.contrib import admin
from .models import CashbackOrder, CashbackService, CashbackOrderService

class CashbackOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'status', 'total_spent_month')

    def total_spent_month(self, obj):
        if obj.status == 'completed':
            return obj.total_spent_month
        return '—'  # Пустое значение для незавершенных заявок
    total_spent_month.short_description = 'Общая трата за месяц'

    def save_model(self, request, obj, form, change):
        # Пересчитываем общую сумму при сохранении заявки
        obj.calculate_total_spent()
        super().save_model(request, obj, form, change)

admin.site.register(CashbackOrder, CashbackOrderAdmin)
admin.site.register(CashbackService)
admin.site.register(CashbackOrderService)

