from rest_framework import serializers
from .models import CashbackService, CashbackOrder, CashbackOrderService
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import AuthUser

class CashbackServiceSerializer(serializers.ModelSerializer):
    # Делаем поле image_url необязательным
    image_url = serializers.CharField(required=False)

    class Meta:
        model = CashbackService
        fields = '__all__'

class CashbackOrderSerializer(serializers.ModelSerializer):
    services = CashbackServiceSerializer(many=True, read_only=True)

    class Meta:
        model = CashbackOrder
        fields = '__all__'

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
# from rest_framework import serializers
# from .models import CashbackService, CashbackOrder, CashbackOrderService
# from django.contrib.auth.models import User

# class CashbackServiceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CashbackService
#         fields = '__all__'

# class CashbackOrderSerializer(serializers.ModelSerializer):
#     services = CashbackServiceSerializer(many=True, read_only=True)

#     class Meta:
#         model = CashbackOrder
#         fields = '__all__'

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username', 'password']

#     def create(self, validated_data):
#         user = User(**validated_data)
#         user.set_password(validated_data['password'])
#         user.save()
#         return user

