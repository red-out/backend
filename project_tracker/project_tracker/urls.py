from django.contrib import admin
from django.urls import path
from tasks import views

urlpatterns = [
    path('', views.hello, name='home'),  # Главная страница с карточками
    path('order/<int:id>/', views.GetOrder, name='order_url'),  # Детали заказа
    path('cart/', views.cart, name='cart'),  # Страница корзины
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),  # Добавление в корзину
    path('clear-cart/', views.clear_cart, name='clear_cart'),  # Очистка корзины
    
]





