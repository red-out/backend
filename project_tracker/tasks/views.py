from datetime import datetime
from django.db import IntegrityError  
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging
from .authentication import RedisSessionAuthentication
from django.db import connection
from rest_framework.decorators import action
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from tasks.permissions import IsAdmin, IsManager
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .models import CashbackService, CashbackOrder, CashbackOrderService, CustomUser
from .serializers import (
    CashbackOrderServiceSerializer, 
    CompleteOrRejectOrderSerializer, 
    CashbackServiceSerializer, 
    CashbackOrderSerializer, 
    UserSerializer
)
from .minio import add_pic, delete_pic
from .singleton import UserSingleton
import redis
import uuid
from django.http import HttpResponse, JsonResponse
REDIS_HOST = 'localhost'
REDIS_PORT = 6379


# Connect to our Redis instance
session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

# def get_creator():
#     return UserSingleton.get_instance().get_user()  # Получаем фиксированного пользователя

# ЛАБА 4

class UserViewSet(viewsets.ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def create(self, request):
        """
        Функция регистрации новых пользователей
        Если пользователя c указанным в request email ещё нет, в БД будет добавлен новый пользователь.
        """
        if self.model_class.objects.filter(email=request.data['email']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            self.model_class.objects.create_user(email=serializer.data['email'],
                                     password=serializer.data['password'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes        
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

@swagger_auto_schema(method='patch', request_body=UserSerializer)
@api_view(['PATCH'])
@permission_classes([AllowAny])
def partial_update(request, pk=None):
    """
    Метод для частичного обновления данных пользователя.
    """
    try:
        user = CustomUser.objects.get(pk=pk)  # Используйте правильный класс модели
    except CustomUser.DoesNotExist:
        return Response({'status': 'Error', 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)  # Используйте правильный сериализатор
    if serializer.is_valid():
        serializer.save()
        return Response({'status': 'Success', 'data': serializer.data}, status=status.HTTP_200_OK)
    
    return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data["email"] 
    password = request.data["password"]
    user = authenticate(request, email=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        
        # Генерация session_id
        random_key = str(uuid.uuid4())
        
        # Сохранение в Redis
        session_storage.set(random_key, username)
        
        # Лог для отладки
        print(f"Generated session_id: {random_key}")
        
        # Создание ответа
        response = JsonResponse({
            'status': 'ok',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
        
        # Установка session_id в cookie
        response.set_cookie("session_id", random_key, path="/")

        return response
    else:
        return HttpResponse("{'status': 'error', 'error': 'login failed'}")

@api_view(['Post'])
def logout_view(request):
    logout(request._request)
    return Response({'status': 'Success'})

# ЛАБА 4 КОНЕЦ


class CashbackServiceList(APIView):
   #authentication_classes = [JWTAuthentication]  # Enable JWT Authentication
    authentication_classes = [RedisSessionAuthentication]  # Enable JWT Authentication
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]  # Разрешить всем пользователям на POST
        elif self.request.method == 'GET':
            return [AllowAny()]  # Разрешить только администраторам на GET
        return super().get_permissions()  # Для других методов использовать стандартные разрешения

    def get(self, request):
        self.check_permissions(request)
        creator = request.user
        services = CashbackService.objects.filter(status='active')

        draft_order = CashbackOrder.objects.filter(creator=creator, status='draft').first()
        draft_order_id = draft_order.id if draft_order else None

        services_count = CashbackOrderService.objects.filter(order=draft_order).count() if draft_order else 0

        response_data = []
        for service in services:
            service_data = {
                "id": service.id,
                "image_url": service.image_url,
                "category": service.category,
                "cashback_percentage_text": service.cashback_percentage_text,
                "full_description": service.full_description,
                "details": service.details,
                "status": service.status,
            }
            response_data.append(service_data)

        response_data.append({
            "draft_order_id": draft_order_id,
            "cashbacks_count": services_count
        })

        return Response(response_data)

    @swagger_auto_schema(request_body=CashbackServiceSerializer)
    def post(self, request):
        self.check_permissions(request)  # Явно проверяем права доступа
        serializer = CashbackServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Сохраняем новую услугу
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CashbackServiceDetail(APIView):
    authentication_classes = [RedisSessionAuthentication]  # Enable JWT Authentication
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdmin()]  # Разрешить всем пользователям на POST
        elif self.request.method == 'PUT':
            return [IsAdmin()]  # Разрешить только администраторам на GET
        return super().get_permissions()  # Для других методов использовать стандартные разрешения

    def get(self, request, id):
        service = get_object_or_404(CashbackService, id=id)
        serializer = CashbackServiceSerializer(service)
        return Response(serializer.data)
    
    @swagger_auto_schema(request_body=CashbackServiceSerializer)
    def put(self, request, id):
        service = get_object_or_404(CashbackService, id=id)
        serializer = CashbackServiceSerializer(service, data=request.data, partial=True)

        if 'pic' in request.FILES:
            pic_result = add_pic(service, request.FILES['pic'])
            if 'error' in pic_result.data:
                return pic_result

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        service = get_object_or_404(CashbackService, id=id)

        # Удаляем изображение из MinIO
        pic_result = delete_pic(service)
        if 'error' in pic_result:
            return Response(pic_result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Изменяем статус на 'deleted'
        service.status = 'deleted'
        service.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    

    @csrf_exempt
    @swagger_auto_schema(method='post')
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def add_to_draft_order(request, id):
        user = request.user

      #  if not user.is_authenticated:
       #     return Response({'error': 'Пользователь не аутентифицирован'}, status=status.HTTP_401_UNAUTHORIZED)

    # Проверяем существование пользователя
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM tasks_customuser WHERE id = %s", [user.id])
            result = cursor.fetchone()

        if not result:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        email = result[0]
        service = get_object_or_404(CashbackService, id=id)

    # Проверяем существующий черновик
        draft_order = CashbackOrder.objects.filter(creator=user, status='draft').first()

    # Если черновик не существует, создаем новый
        if not draft_order:
            draft_order = CashbackOrder.objects.create(creator=user, status='draft')

    # Добавляем услугу в черновик
        CashbackOrderService.objects.create(order=draft_order, service=service)

        return Response({'order_id': draft_order.id}, status=status.HTTP_201_CREATED)
 

    @swagger_auto_schema(method='post')
    @api_view(['POST'])
    @permission_classes([IsAdmin])
    def add_image(request, id):
        service = get_object_or_404(CashbackService, id=id)
        pic = request.FILES.get("pic")
        pic_result = add_pic(service, pic)
        if 'error' in pic_result.data:
            return pic_result
        return Response({'message': 'Image added successfully'}, status=status.HTTP_200_OK)


class CashbackOrderList(APIView):
    authentication_classes = [RedisSessionAuthentication]  # Enable JWT Authentication
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]  # Разрешить всем пользователям на POST
        elif self.request.method == 'GET':
            return [AllowAny()]  # Разрешить только администраторам на GET
        return super().get_permissions()  # Для других методов использовать стандартные разрешения
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Пользователь не авторизован'}, status=status.HTTP_403_FORBIDDEN)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')

    # Получаем заявки с исключением статусов "deleted" и "draft"
        orders = CashbackOrder.objects.exclude(status__in=['deleted', 'draft'])

    # Если пользователь не является менеджером, фильтруем только по его заявкам
        if not request.user.has_perm('tasks.IsManager'):
            orders = orders.filter(creator=request.user)  # Заявки только текущего пользователя

    # Фильтрация по дате начала
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                orders = orders.filter(formation_date__gte=start_date)
            except ValueError:
                return Response({'error': 'Invalid start date format'}, status=status.HTTP_400_BAD_REQUEST)

    # Фильтрация по дате окончания
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                orders = orders.filter(formation_date__lte=end_date)
            except ValueError:
                return Response({'error': 'Invalid end date format'}, status=status.HTTP_400_BAD_REQUEST)

    # Фильтрация по статусу
        if status_filter:
            orders = orders.filter(status=status_filter)

    # Сортировка по статусу
        orders = orders.order_by('status')

    # Используем select_related для оптимизации запросов к creator и moderator
        serializer = CashbackOrderSerializer(orders.select_related('creator', 'moderator'), many=True)
        return Response(serializer.data)


class CashbackOrderDetail(APIView):
    authentication_classes = [RedisSessionAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        order = get_object_or_404(CashbackOrder, id=id)
        services = CashbackOrderService.objects.filter(order=order).select_related('service')
        order_data = {
            "id": order.id,
            "status": order.status,
            "creation_date": order.creation_date,
            "formation_date": order.formation_date,
            "completion_date": order.completion_date,
            "month": order.month,
            "total_spent_month": order.total_spent_month,
            "creator": order.creator.email,  
            "moderator": order.moderator.email if order.moderator else None,
            "services": [
                {
                    "service_id": service.service.id,
                    "category": service.service.category,
                    "image_url": service.service.image_url,
                    "total_spent": service.total_spent
                }
                for service in services
            ]
        }
        return Response(order_data)
    
    @swagger_auto_schema(request_body=CashbackOrderSerializer)
    def put(self, request, id):
        print(f"Received ID: {id}")
        order = get_object_or_404(CashbackOrder, id=id)
        serializer = CashbackOrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(method='put')
    @api_view(['PUT'])
    def create_order(request, id):
        order = get_object_or_404(CashbackOrder, id=id, status='draft')

    # Проверяем, заполнено ли поле "месяц" в заказе
        if not order.month:
            return Response({'error': 'Поле "месяц" должно быть заполнено.'}, status=status.HTTP_400_BAD_REQUEST)

    # Логика для обновления заказа
        order.status = 'formed'
        order.formation_date = timezone.now()  # Устанавливаем дату формирования
        order.save()

        return Response(status=status.HTTP_200_OK)
    

    
class CashbackOrderServiceList(APIView):
    
    def delete(self, request, order_id, service_id):
        order_service = get_object_or_404(CashbackOrderService, order_id=order_id, service_id=service_id)
        order_service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=CashbackOrderServiceSerializer)
    def put(self, request, order_id, service_id):
        order_service = get_object_or_404(CashbackOrderService, order_id=order_id, service_id=service_id)
        serializer = CashbackOrderServiceSerializer(data=request.data)

        if serializer.is_valid():
            order_service.total_spent = serializer.validated_data['total_spent']
            order_service.save()
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
class Complete(APIView):
   #authentication_classes = [JWTAuthentication]  # Enable JWT Authentication
    authentication_classes = [RedisSessionAuthentication]  # Enable JWT Authentication
    def get_permissions(self):
        if self.request.method == 'PUT':
            return [IsManager()]  # Разрешить всем пользователям на POST
        elif self.request.method == 'GET':
            return [AllowAny()]  # Разрешить только администраторам на GET
        return super().get_permissions()  # Для других методов использовать стандартные разрешения

    @swagger_auto_schema(request_body=CompleteOrRejectOrderSerializer)
    def put(self, request, id):  # 'id' передается через kwargs
        # Получаем объект CashbackOrder или возвращаем 404
        order = get_object_or_404(CashbackOrder, id=id)
        
        # Десериализуем входные данные
        serializer = CompleteOrRejectOrderSerializer(data=request.data)

        # Проверяем валидность данных
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action = serializer.validated_data['action']

        # Обновляем статус заказа в зависимости от действия
        if action == 'complete':
            order.status = 'completed'
            order.completion_date = timezone.now()  # Устанавливаем дату завершения
            order.moderator = request.user  # Устанавливаем объект авторизованного пользователя
            
            order.calculate_total_spent()  # Вычисляем общую сумму
        elif action == 'reject':  # Если действие 'reject'
            order.status = 'rejected'
            order.moderator = request.user  # Устанавливаем объект авторизованного пользователя  
            order.completion_date = timezone.now()  # Устанавливаем дату завершения
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        # Сохраняем изменения в заказе
        order.save()
        return Response(status=status.HTTP_200_OK)