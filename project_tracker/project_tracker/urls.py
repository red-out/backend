from django.urls import path
from tasks import views

urlpatterns = [
    path('', views.all_cashback_services, name='home'),  # Главная страница с кешбэк-услугами
    path('cashback/<int:id>/', views.cashback_details, name='cashback_details'),  # Детали кешбэк-услуги
    path('your_cashbacks/<int:report_id>/', views.monthly_cashbacks_view, name='monthly_cashbacks'),  # Страница с кешбэками за месяц
]



