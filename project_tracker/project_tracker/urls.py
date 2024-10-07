from django.contrib import admin
from django.urls import path
from tasks.views import (
    CashbackServiceList,
    CashbackServiceDetail,
    CashbackOrderList,
    CashbackOrderDetail,
    CashbackOrderServiceList,
    UserRegistration,
    UserProfile,
    login,
    logout,
)

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),  # URL для админки

    # Домен услуги
    path('cashback_services/', CashbackServiceList.as_view(), name='cashback_service_list'),  # Получить список услуг
    path('cashback_services/<int:id>/', CashbackServiceDetail.as_view(), name='cashback_service_detail'),  # Получить одну услугу
    path('cashback_services/add/', CashbackServiceList.as_view(), name='cashback_service_add'),  # Добавить новую услугу
    path('cashback_services/<int:id>/update/', CashbackServiceDetail.as_view(), name='cashback_service_update'),  # Изменить услугу
    path('cashback_services/<int:id>/delete/', CashbackServiceDetail.as_view(), name='cashback_service_delete'),  # Удалить услугу
    path('cashback_services/<int:id>/add_to_draft/', CashbackServiceDetail.add_to_draft_order, name='add_to_draft_order'),  # Добавить в черновик
    path('cashback_services/<int:id>/add_image/', CashbackServiceDetail.add_image, name='add_image'),  # Добавить изображение

    # Домен заявки
    path('cashback_orders/', CashbackOrderList.as_view(), name='cashback_order_list'),  # Получить список заявок
    path('cashback_orders/<int:id>/', CashbackOrderDetail.as_view(), name='cashback_order_detail'),  # Получить заявку
    path('cashback_orders/<int:id>/update/', CashbackOrderDetail.put, name='cashback_order_update'),  # Изменить заявку
    path('cashback_orders/<int:id>/create/', CashbackOrderDetail.create_order, name='create_order'),  # Сформировать заявку
    path('cashback_orders/<int:id>/complete_or_reject/', CashbackOrderDetail.complete_or_reject_order, name='complete_or_reject_order'),  # Завершить/отклонить заявку
    path('cashback_orders/<int:id>/delete/', CashbackOrderDetail.delete, name='cashback_order_delete'),  # Удалить заявку

    # Домен м-м
    path('cashback_orders/<int:order_id>/services/<int:service_id>/delete/', CashbackOrderServiceList.delete, name='order_service_delete'),  # Удалить услугу из заявки
    path('cashback_orders/<int:order_id>/services/<int:service_id>/update/', CashbackOrderServiceList.put, name='order_service_update'),  # Изменить услугу в заявке

    # Домен пользователь
    path('register/', UserRegistration.as_view(), name='user_registration'),  # Регистрация
    path('profile/update/', UserProfile.put, name='user_profile_update'),  # Обновление профиля
    path('login/', login, name='login'),  # Аутентификация
    path('logout/', logout, name='logout'),  # Деавторизация
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





