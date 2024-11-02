from django.contrib import admin
from rest_framework import permissions
from drf_yasg import openapi
from django.urls import path, include
from drf_yasg.views import get_schema_view
from tasks.views import (
    CashbackServiceList,
    CashbackServiceDetail,
    CashbackOrderList,
    CashbackOrderDetail,
    CashbackOrderServiceList,
    UserRegistration,
    UserProfile,
    UserLogin,  # Изменено на класс для аутентификации
    UserLogout,  # Изменено на класс для деавторизации
)
schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    #swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # Админка
    path('admin/', admin.site.urls),

    # Домен услуги
    path('cashback_services/', CashbackServiceList.as_view(), name='cashback_service_list'),
    path('cashback_services/<int:id>/', CashbackServiceDetail.as_view(), name='cashback_service_detail'),
    path('cashback_services/add/', CashbackServiceList.as_view(), name='cashback_service_add'),
    path('cashback_services/<int:id>/update/', CashbackServiceDetail.as_view(), name='cashback_service_update'),
    path('cashback_services/<int:id>/delete/', CashbackServiceDetail.as_view(), name='cashback_service_delete'),
    path('cashback_services/<int:id>/add_to_draft/', CashbackServiceDetail.add_to_draft_order, name='add_to_draft_order'),
    path('cashback_services/<int:id>/add_image/', CashbackServiceDetail.add_image, name='add_image'),

    # Домен заявки
    path('cashback_orders/', CashbackOrderList.as_view(), name='cashback_order_list'),
    path('cashback_orders/<int:id>/', CashbackOrderDetail.as_view(), name='cashback_order_detail'),
    path('cashback_orders/<int:id>/update/', CashbackOrderDetail.as_view(), name='cashback_order_update'),
    path('cashback_orders/<int:id>/create/', CashbackOrderDetail.create_order, name='create_order'),
    path('cashback_orders/<int:id>/complete_or_reject/', CashbackOrderDetail.complete_or_reject_order, name='complete_or_reject_order'),
    path('cashback_orders/<int:id>/delete/', CashbackOrderDetail.as_view(), name='cashback_order_delete'),

    # Домен услуг в заявке
    path('cashbacks_orders/<int:order_id>/services/<int:service_id>/delete/', CashbackOrderServiceList.as_view(), name='order_service_delete'),
    path('cashbacks_orders/<int:order_id>/services/<int:service_id>/update/', CashbackOrderServiceList.as_view(), name='order_service_update'),

    # Домен пользователь
    path('auth/register/', UserRegistration.as_view(), name='user_registration'),
    path('auth/profile/update/', UserProfile.as_view(), name='user_profile_update'),
    path('auth/login/', UserLogin.as_view(), name='login'),  # Обновлено на класс
    path('auth/logout/', UserLogout.as_view(), name='logout'),  # Обновлено на класс
]

# from django.contrib import admin
# from django.urls import path
# from tasks.views import (
#     CashbackServiceList,
#     CashbackServiceDetail,
#     CashbackOrderList,
#     CashbackOrderDetail,
#     CashbackOrderServiceList,
#     UserRegistration,
#     UserProfile,
#     login,
#     logout,
# )

# urlpatterns = [
#     # Админка
#     path('admin/', admin.site.urls),  # URL для админки

#     # Домен услуги
#     path('cashback_services/', CashbackServiceList.as_view(), name='cashback_service_list'),  # Получить список услуг
#     path('cashback_services/<int:id>/', CashbackServiceDetail.as_view(), name='cashback_service_detail'),  # Получить одну услугу
#     path('cashback_services/add/', CashbackServiceList.as_view(), name='cashback_service_add'),  # Добавить новую услугу
#     path('cashback_services/<int:id>/update/', CashbackServiceDetail.as_view(), name='cashback_service_update'),  # Изменить услугу
#     path('cashback_services/<int:id>/delete/', CashbackServiceDetail.as_view(), name='cashback_service_delete'),  # Удалить услугу
#     path('cashback_services/<int:id>/add_to_draft/', CashbackServiceDetail.add_to_draft_order, name='add_to_draft_order'),  # Добавить в черновик
#     path('cashback_services/<int:id>/add_image/', CashbackServiceDetail.add_image, name='add_image'),  # Добавить изображение

#     # Домен заявки
#     path('cashback_orders/', CashbackOrderList.as_view(), name='cashback_order_list'),  # Получить список заявок
#     path('cashback_orders/<int:id>/', CashbackOrderDetail.as_view(), name='cashback_order_detail'),  # Получить заявку
#     path('cashback_orders/<int:id>/update/', CashbackOrderDetail.put, name='cashback_order_update'),  # Изменить заявку
#     path('cashback_orders/<int:id>/create/', CashbackOrderDetail.create_order, name='create_order'),  # Сформировать заявку
#     path('cashback_orders/<int:id>/complete_or_reject/', CashbackOrderDetail.complete_or_reject_order, name='complete_or_reject_order'),  # Завершить/отклонить заявку
#     path('cashback_orders/<int:id>/delete/', CashbackOrderDetail.delete, name='cashback_order_delete'),  # Удалить заявку

#     # Домен м-м
#     path('cashback_orders/<int:order_id>/services/<int:service_id>/delete/', CashbackOrderServiceList.delete, name='order_service_delete'),  # Удалить услугу из заявки
#     path('cashback_orders/<int:order_id>/services/<int:service_id>/update/', CashbackOrderServiceList.put, name='order_service_update'),  # Изменить услугу в заявке

#     # Домен пользователь
#     path('register/', UserRegistration.as_view(), name='user_registration'),  # Регистрация
#     path('profile/update/', UserProfile.put, name='user_profile_update'),  # Обновление профиля
#     path('login/', login, name='login'),  # Аутентификация
#     path('logout/', logout, name='logout'),  # Деавторизация
# ]





