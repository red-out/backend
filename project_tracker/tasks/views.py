from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from .models import CashbackService, CashbackOrder, CashbackOrderService
from .serializers import CashbackServiceSerializer, CashbackOrderSerializer, UserSerializer
from .minio import add_pic, delete_pic
from .singleton import UserSingleton
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import AuthUser  # Убедитесь, что путь правильный


def get_creator():
    return UserSingleton.get_instance().get_user()  # Получаем фиксированного пользователя


class CashbackServiceList(APIView):
    def get(self, request):
        creator = get_creator()
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

    def post(self, request):
        serializer = CashbackServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Сохраняем новую услугу
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CashbackServiceDetail(APIView):
    def get(self, request, id):
        service = get_object_or_404(CashbackService, id=id)
        serializer = CashbackServiceSerializer(service)
        return Response(serializer.data)

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
   
    @api_view(['POST'])
    def add_to_draft_order(request, id):
        service = get_object_or_404(CashbackService, id=id)
        creator = get_creator()  # Получаем создателя через функцию-синглтон

    # Пытаемся найти последний черновик, созданный данным пользователем
        draft_order = CashbackOrder.objects.filter(creator=creator, status='draft').last()

    # Если черновик не найден, создаем новый
        if draft_order is None:
            draft_order = CashbackOrder.objects.create(creator=creator, status='draft')

    # Добавляем услугу в черновик (существующий или новый)
        CashbackOrderService.objects.create(order=draft_order, service=service)

    # Возвращаем ID черновика
        return Response({'order_id': draft_order.id}, status=status.HTTP_201_CREATED)

    @api_view(['POST'])
    def add_image(request, id):
        service = get_object_or_404(CashbackService, id=id)
        pic = request.FILES.get("pic")
        pic_result = add_pic(service, pic)
        if 'error' in pic_result.data:
            return pic_result
        return Response({'message': 'Image added successfully'}, status=status.HTTP_200_OK)


class CashbackOrderList(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')

        orders = CashbackOrder.objects.exclude(status__in=['deleted', 'draft'])

        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                orders = orders.filter(formation_date__gte=start_date)
            except ValueError:
                return Response({'error': 'Invalid start date format'}, status=status.HTTP_400_BAD_REQUEST)

        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                orders = orders.filter(formation_date__lte=end_date)
            except ValueError:
                return Response({'error': 'Invalid end date format'}, status=status.HTTP_400_BAD_REQUEST)

        if status_filter:
            orders = orders.filter(status=status_filter)        # Фильтрация по статусу
       
        # Сортировка по статусу
        orders = orders.order_by('status')

        serializer = CashbackOrderSerializer(orders.select_related('creator', 'moderator'), many=True)
        return Response(serializer.data)


class CashbackOrderDetail(APIView):
    def get(self, request, id):
        order = get_object_or_404(CashbackOrder, id=id)
        services = CashbackOrderService.objects.filter(order=order).select_related('service')
        order_data = CashbackOrderSerializer(order).data
        order_data['services'] = [{'service_id': service.service.id, 'category': service.service.category, 'image_url': service.service.image_url, 'total_spent': service.total_spent} for service in services]
        return Response(order_data)

    def put(self, request, id):
        print(f"Received ID: {id}")
        order = get_object_or_404(CashbackOrder, id=id)
        serializer = CashbackOrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    @api_view(['PUT'])
    def complete_or_reject_order(request, id):
        order = get_object_or_404(CashbackOrder, id=id)
        action = request.data.get('action')
        if action not in ['complete', 'reject']:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'complete':
            order.status = 'completed'
            order.completion_date = timezone.now()  # Устанавливаем дату завершения
            order.moderator = get_creator()  # Устанавливаем модератора
            
            order.calculate_total_spent()  
        else:  # reject
            order.status = 'rejected'
            order.moderator = get_creator()  
            order.completion_date = timezone.now()  # Устанавливаем дату завершения

        order.save()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, id):
        order = get_object_or_404(CashbackOrder, id=id)
        order.formation_date = timezone.now()  # Устанавливаем дату формирования
        order.status = 'deleted'
        order.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CashbackOrderServiceList(APIView):
    def delete(self, request, order_id, service_id):
        order_service = get_object_or_404(CashbackOrderService, order_id=order_id, service_id=service_id)
        order_service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, order_id, service_id):
        order_service = get_object_or_404(CashbackOrderService, order_id=order_id, service_id=service_id)
        total_spent = request.data.get('total_spent')
        if total_spent is not None:
            order_service.total_spent = total_spent
            order_service.save()
            return Response(status=status.HTTP_200_OK)
        return Response({'error': 'Total_spent is required'}, status=status.HTTP_400_BAD_REQUEST)



class UserRegistration(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        user = AuthUser(
            username=username,
            password=password,  
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.save()
        return Response({'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)


class UserProfile(APIView):
    def put(self, request):
        user = get_creator()  # Получаем фиксированного создателя
        # Обновляем поля пользователя
        for attr, value in request.data.items():
            setattr(user, attr, value)
        user.save()
        return Response({'id': user.id, 'username': user.username}, status=status.HTTP_200_OK)


class UserLogin(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            user = AuthUser.objects.get(username=username)
            if user.password == password:  # Проверяем пароль напрямую
                auth_login(request, user)  
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except AuthUser.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogout(APIView):
    def post(self, request):
        auth_logout(request)  # Завершаем сессию
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)