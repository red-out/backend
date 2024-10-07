from rest_framework import serializers
from .models import CashbackService, CashbackOrder, CashbackOrderService
from django.contrib.auth.models import User

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

