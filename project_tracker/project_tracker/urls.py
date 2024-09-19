from django.contrib import admin
from django.urls import path
from tasks import views

urlpatterns = [
    path('', views.cashback_services, name='home'),  # Главная страница с карточками
    path('cashback/<int:id>/', views.GetOrder, name='cashback_url'),  # Детали заказа
    path('your_cashbacks/', views.categories_cashbacks_view, name='cart'),  # Страница корзины
 
]







