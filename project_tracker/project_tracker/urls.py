
from django.urls import path
from tasks import views
from django.contrib import admin
urlpatterns = [
    path('', views.cashback_services, name='home'),  # Главная страница с карточками
    path('cashback/<int:id>/', views.GetOrder, name='cashback_url'),  # Детали заказа
    path('your_cashbacks/<int:order_id>/', views.categories_cashbacks_view, name='cart'),
       path('admin/', admin.site.urls),  # Страница корзины с order_id
]



