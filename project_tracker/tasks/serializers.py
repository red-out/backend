from rest_framework import serializers
from .models import CashbackService, CashbackOrder, CashbackOrderService
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import AuthUser
from collections import OrderedDict
from tasks.models import CustomUser

class CashbackServiceSerializer(serializers.ModelSerializer):
    # Делаем поле image_url необязательным
    image_url = serializers.CharField(required=False)

    class Meta:
        model = CashbackService
        fields = '__all__'

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields
    
class CashbackOrderSerializer(serializers.ModelSerializer):
    services = CashbackServiceSerializer(many=True, read_only=True)

    class Meta:
        model = CashbackOrder
        fields = '__all__'

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields

class UserSerializer(serializers.ModelSerializer):
    # Переопределяем поле password, чтобы оно не было видно в ответе
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        # Создаём пользователя с хэшированным паролем
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        # Хешируем пароль перед сохранением
        validated_data['password'] = make_password(validated_data['password'])
        user = AuthUser(**validated_data)
        user.save()
        return user

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields
# только для сваггера
class CompleteOrRejectOrderSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['complete', 'reject'])
# только для сваггера
class CashbackOrderServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashbackOrderService
        fields = ['total_spent']  
#для авторизации
class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'is_staff', 'is_superuser']
