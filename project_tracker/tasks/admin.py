from django.contrib import admin
from .models import CashbackOrder, CashbackService, CashbackOrderService

class CashbackOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'status', 'total_spent')  # добавляем total_spent

    def total_spent(self, obj):
        return sum(service.total_spent for service in obj.cashbackorderservice_set.all())  # вычисляем общую сумму
    total_spent.short_description = 'Общая сумма'

admin.site.register(CashbackOrder, CashbackOrderAdmin)
admin.site.register(CashbackService)
admin.site.register(CashbackOrderService)

# from django.contrib import admin
# from .models import CashbackService, CashbackOrder, CashbackOrderService

# class CashbackOrderServiceInline(admin.TabularInline):
#     model = CashbackOrderService
#     extra = 1

# class CashbackOrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'creator', 'status', 'total_spent', 'creation_date')
#     list_filter = ('status',)
#     inlines = [CashbackOrderServiceInline]

# admin.site.register(CashbackService)
# admin.site.register(CashbackOrder, CashbackOrderAdmin)
# admin.site.register(CashbackOrderService)
