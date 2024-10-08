from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from .models import CashbackService, CashbackOrder, CashbackOrderService
from .serializers import CashbackServiceSerializer, CashbackOrderSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from .minio import add_pic, delete_pic  # Импортируем функции для работы с изображениями
from django.utils import timezone
from datetime import datetime

# Домен услуги
class CashbackServiceList(APIView):
    def get(self, request):
        services = CashbackService.objects.filter(status='active')

        for service in services:
            service.draft_order_id = CashbackOrder.objects.filter(creator=None, status='draft').values('id').first()

        # Фильтрация по категории, если указана
        category_filter = request.query_params.get('category')
        if category_filter:
            services = services.filter(category=category_filter)

        serializer = CashbackServiceSerializer(services, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CashbackServiceSerializer(data=request.data)
        if serializer.is_valid():
            stock = serializer.save()  # Сохраняем объект услуги

            pic = request.FILES.get("pic")  # Извлекаем файл изображения
            pic_result = add_pic(stock, pic)  # Добавляем изображение

            # Если в результате вызова add_pic результат - ошибка, возвращаем его.
            if 'error' in pic_result.data:
                return pic_result

            # Возвращаем данные с URL изображения
            return Response(CashbackServiceSerializer(stock).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CashbackServiceDetail(APIView):
    def get(self, request, id):
        service = get_object_or_404(CashbackService, id=id)
        serializer = CashbackServiceSerializer(service)
        return Response(serializer.data)

    def put(self, request, id):
        service = get_object_or_404(CashbackService, id=id)
        serializer = CashbackServiceSerializer(service, data=request.data, partial=True)

        if 'pic' in request.FILES:  # Проверяем, есть ли файл изображения
            pic_result = add_pic(service, request.FILES['pic'])  # Добавляем изображение
            if 'error' in pic_result.data:
                return pic_result  # Если есть ошибка, возвращаем её

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        service = get_object_or_404(CashbackService, id=id)

        # Удаляем изображение, если оно есть
        if service.image_url:
            image_name = f"{service.id}.png"  # Извлекаем имя файла на основе ID услуги
            delete_result = delete_pic(image_name)  # Удаляем изображение из MinIO

            # Проверяем результат удаления
            if 'error' in delete_result:
                return Response(delete_result, status=status.HTTP_400_BAD_REQUEST)

        # Обновляем статус услуги на "deleted"
        service.status = 'deleted'
        service.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @api_view(['POST'])
    def add_to_draft_order(request, id):
        service = get_object_or_404(CashbackService, id=id)

        # Получаем текущего пользователя
        user = request.user

        # Проверяем, авторизован ли пользователь
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Создаем или получаем существующий заказ в статусе 'draft' для данного пользователя
        order, created = CashbackOrder.objects.get_or_create(
            creator=user,
            status='draft'
        )

        # Добавляем услугу в заявку
        CashbackOrderService.objects.create(order=order, service=service, quantity=1)

        return Response({'order_id': order.id}, status=status.HTTP_201_CREATED)

    @api_view(['POST'])
    def add_image(request, id):
        service = get_object_or_404(CashbackService, id=id)
        pic = request.FILES.get("pic")
        pic_result = add_pic(service, pic)  # Используем функцию для добавления изображения
        if 'error' in pic_result.data:
            return pic_result
        return Response({'message': 'Image added successfully'}, status=status.HTTP_200_OK)

# Домен заявки
class CashbackOrderList(APIView):
    def get(self, request):
        # Фильтрация по дате формирования и статусу
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        status_filter = request.query_params.get('status')

        orders = CashbackOrder.objects.exclude(status='deleted')

        if date_from:
            orders = orders.filter(created_at__gte=datetime.strptime(date_from, '%Y-%m-%d'))
        if date_to:
            orders = orders.filter(created_at__lte=datetime.strptime(date_to, '%Y-%m-%d'))
        if status_filter:
            orders = orders.filter(status=status_filter)

        serializer = CashbackOrderSerializer(orders, many=True)
        return Response(serializer.data)

class CashbackOrderDetail(APIView):
    def get(self, request, id):
        order = get_object_or_404(CashbackOrder, id=id)
        serializer = CashbackOrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, id):
        order = get_object_or_404(CashbackOrder, id=id)
        serializer = CashbackOrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @api_view(['PUT'])
    def create_order(request, id):
        order = get_object_or_404(CashbackOrder, id=id, status='draft')
        required_fields = ['total_spent_month']
        if any(not getattr(order, field) for field in required_fields):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'formed'
        order.save()
        return Response(status=status.HTTP_200_OK)

    @api_view(['PUT'])
    def complete_or_reject_order(request, id):
        order = get_object_or_404(CashbackOrder, id=id)
        action = request.data.get('action')
        if action not in ['complete', 'reject']:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'completed' if action == 'complete' else 'rejected'
        order.save()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, id):
        order = get_object_or_404(CashbackOrder, id=id)
        order.status = 'deleted'
        order.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Домен м-м
class CashbackOrderServiceList(APIView):
    def delete(self, request, order_id, service_id):
        order_service = get_object_or_404(CashbackOrderService, order_id=order_id, service_id=service_id)
        order_service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, order_id, service_id):
        order_service = get_object_or_404(CashbackOrderService, order_id=order_id, service_id=service_id)
        quantity = request.data.get('quantity')
        if quantity is not None:
            order_service.quantity = quantity
            order_service.save()
            return Response(status=status.HTTP_200_OK)
        return Response({'error': 'Quantity is required'}, status=status.HTTP_400_BAD_REQUEST)

# Домен пользователь
class UserRegistration(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfile(APIView):
    def put(self, request):
        user = request.user  # Мы можем игнорировать аутентификацию
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'id': user.id, 'username': user.username}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Аутентификация и деавторизация
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout(request):
    if request.user.is_authenticated:
        request.user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)

# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework import status
# from django.shortcuts import get_object_or_404
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from rest_framework.decorators import api_view
# from .models import CashbackService, CashbackOrder, CashbackOrderService
# from .serializers import CashbackServiceSerializer, CashbackOrderSerializer, UserSerializer
# from rest_framework.authtoken.models import Token
# from .minio import add_pic, delete_pic  # Импортируем функции для работы с изображениями
# from django.utils import timezone
# from datetime import datetime

# # Домен услуги
# class CashbackServiceList(APIView):
#     def get(self, request):
#         services = CashbackService.objects.filter(status='active')

#         for service in services:
#             service.draft_order_id = CashbackOrder.objects.filter(creator=None, status='draft').values('id').first()

#         # Фильтрация по категории, если указана
#         category_filter = request.query_params.get('category')
#         if category_filter:
#             services = services.filter(category=category_filter)

#         serializer = CashbackServiceSerializer(services, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = CashbackServiceSerializer(data=request.data)
#         if serializer.is_valid():
#             stock = serializer.save()  # Сохраняем объект услуги

#             pic = request.FILES.get("pic")  # Извлекаем файл изображения
#             pic_result = add_pic(stock, pic)  # Добавляем изображение

#             # Если в результате вызова add_pic результат - ошибка, возвращаем его.
#             if 'error' in pic_result.data:
#                 return pic_result

#             # Возвращаем данные с URL изображения
#             return Response(CashbackServiceSerializer(stock).data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CashbackServiceDetail(APIView):
#     def get(self, request, id):
#         service = get_object_or_404(CashbackService, id=id)
#         serializer = CashbackServiceSerializer(service)
#         return Response(serializer.data)

#     def put(self, request, id):
#         service = get_object_or_404(CashbackService, id=id)
#         serializer = CashbackServiceSerializer(service, data=request.data, partial=True)

#         if 'pic' in request.FILES:  # Проверяем, есть ли файл изображения
#             pic_result = add_pic(service, request.FILES['pic'])  # Добавляем изображение
#             if 'error' in pic_result.data:
#                 return pic_result  # Если есть ошибка, возвращаем её

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, id):
#         service = get_object_or_404(CashbackService, id=id)

#         # Удаляем изображение, если оно есть
#         if service.image_url:
#             image_name = f"{service.id}.png"  # Извлекаем имя файла на основе ID услуги
#             delete_result = delete_pic(image_name)  # Удаляем изображение из MinIO

#             # Проверяем результат удаления
#             if 'error' in delete_result:
#                 return Response(delete_result, status=status.HTTP_400_BAD_REQUEST)

#         # Обновляем статус услуги на "deleted"
#         service.status = 'deleted'
#         service.save()

#         return Response(status=status.HTTP_204_NO_CONTENT)

#     @api_view(['POST'])
#     def add_to_draft_order(request, id):
#         service = get_object_or_404(CashbackService, id=id)
#         order = CashbackOrder.objects.create(creator=None, status='draft')  # Создаем заказ без пользователя
#         CashbackOrderService.objects.create(order=order, service=service, quantity=1)
#         return Response({'order_id': order.id}, status=status.HTTP_201_CREATED)

#     @api_view(['POST'])
#     def add_image(request, id):
#         service = get_object_or_404(CashbackService, id=id)
#         pic = request.FILES.get("pic")
#         pic_result = add_pic(service, pic)  # Используем функцию для добавления изображения
#         if 'error' in pic_result.data:
#             return pic_result
#         return Response({'message': 'Image added successfully'}, status=status.HTTP_200_OK)

# # Домен заявки
# class CashbackOrderList(APIView):
#     def get(self, request):
#         # Фильтрация по дате формирования и статусу
#         date_from = request.query_params.get('date_from')
#         date_to = request.query_params.get('date_to')
#         status_filter = request.query_params.get('status')

#         orders = CashbackOrder.objects.exclude(status='deleted')

#         if date_from:
#             orders = orders.filter(created_at__gte=datetime.strptime(date_from, '%Y-%m-%d'))
#         if date_to:
#             orders = orders.filter(created_at__lte=datetime.strptime(date_to, '%Y-%m-%d'))
#         if status_filter:
#             orders = orders.filter(status=status_filter)

#         serializer = CashbackOrderSerializer(orders, many=True)
#         return Response(serializer.data)

# class CashbackOrderDetail(APIView):
#     def get(self, request, id):
#         order = get_object_or_404(CashbackOrder, id=id)
#         serializer = CashbackOrderSerializer(order)
#         return Response(serializer.data)

#     def put(self, request, id):
#         order = get_object_or_404(CashbackOrder, id=id)
#         serializer = CashbackOrderSerializer(order, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @api_view(['PUT'])
#     def create_order(request, id):
#         order = get_object_or_404(CashbackOrder, id=id, status='draft')
#         required_fields = ['total_spent_month']
#         if any(not getattr(order, field) for field in required_fields):
#             return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
#         order.status = 'formed'
#         order.save()
#         return Response(status=status.HTTP_200_OK)

#     @api_view(['PUT'])
#     def complete_or_reject_order(request, id):
#         order = get_object_or_404(CashbackOrder, id=id)
#         action = request.data.get('action')
#         if action not in ['complete', 'reject']:
#             return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

#         order.status = 'completed' if action == 'complete' else 'rejected'
#         order.save()
#         return Response(status=status.HTTP_200_OK)

#     def delete(self, request, id):
#         order = get_object_or_404(CashbackOrder, id=id)
#         order.status = 'deleted'
#         order.save()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# # Домен м-м
# class CashbackOrderServiceList(APIView):
#     def delete(self, request, order_id, service_id):
#         order_service = get_object_or_404(CashbackOrderService, order_id=order_id, service_id=service_id)
#         order_service.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

#     def put(self, request, order_id, service_id):
#         order_service = get_object_or_404(CashbackOrderService, order_id=order_id, service_id=service_id)
#         quantity = request.data.get('quantity')
#         if quantity is not None:
#             order_service.quantity = quantity
#             order_service.save()
#             return Response(status=status.HTTP_200_OK)
#         return Response({'error': 'Quantity is required'}, status=status.HTTP_400_BAD_REQUEST)

# # Домен пользователь
# class UserRegistration(APIView):
#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             return Response({'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class UserProfile(APIView):
#     def put(self, request):
#         user = request.user  # Мы можем игнорировать аутентификацию
#         serializer = UserSerializer(user, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'id': user.id, 'username': user.username}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # Аутентификация и деавторизация
# @api_view(['POST'])
# def login(request):
#     username = request.data.get('username')
#     password = request.data.get('password')
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({'token': token.key}, status=status.HTTP_200_OK)
#     return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def logout(request):
#     if request.user.is_authenticated:
#         request.user.auth_token.delete()
#     return Response(status=status.HTTP_200_OK)

