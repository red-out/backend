from django.urls import path
from tasks import views
from django.contrib import admin

urlpatterns = [
    path('', views.all_cashback_services, name='home'),  # Главная страница с кешбэк-услугами
    path('cashback/<int:id>/', views.cashback_details, name='cashback_details'),  # Детали кешбэк-услуги
    path('add_cashback/<int:id>/', views.add_cashback, name='add_cashback'),  # Добавление кешбэка
    path('your_cashbacks/<int:report_id>/', views.monthly_cashbacks_view, name='monthly_cashbacks'),  # Страница с кешбэками за месяц
    path('your_cashbacks/delete/<int:report_id>/', views.delete_cashback_order, name='delete_cashback_order'),  # Удаление заявки
    path('admin/', admin.site.urls),
]





