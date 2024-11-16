from django.contrib import admin
from rest_framework import routers
from rest_framework import permissions
from drf_yasg import openapi
from django.urls import path, include
from drf_yasg.views import get_schema_view
from tasks.views import (
    Complete,
    CashbackServiceList,
    CashbackServiceDetail,
    CashbackOrderList,
    CashbackOrderDetail,
    CashbackOrderServiceList,
    UserViewSet, # 4(laba)
    login_view,
    logout_view,
    partial_update,
  #  complete_or_reject_order,
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
router = routers.DefaultRouter()
router.register(r'user', UserViewSet, basename='user')

# router.register(r'user', views.UserViewSet, basename='user')

urlpatterns = [
    #swagger 
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    #registration (4 laba)
    path('api/', include(router.urls)),
    path('login/',  login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('user/<int:pk>/update/', partial_update, name='user_update'),
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
     path('cashback_orders/<int:id>/complete_or_reject/', Complete.as_view(), name='complete_or_reject_order'),  # Указываем на использование класса
   #  path('cashback_orders/<int:id>/complete_or_reject/', complete_or_reject_order, name='complete_or_reject_order'),
    path('cashback_orders/<int:id>/delete/', CashbackOrderDetail.as_view(), name='cashback_order_delete'),

    # Домен услуг в заявке
    path('cashbacks_orders/<int:order_id>/services/<int:service_id>/delete/', CashbackOrderServiceList.as_view(), name='order_service_delete'),
    path('cashbacks_orders/<int:order_id>/services/<int:service_id>/update/', CashbackOrderServiceList.as_view(), name='order_service_update'),


]

