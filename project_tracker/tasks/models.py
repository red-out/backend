from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from rest_framework import serializers
class CashbackService(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('deleted', 'Удален'),
    ]

    category = models.CharField(max_length=255)
    image_url = models.URLField()
    cashback_percentage_text = models.CharField(max_length=255)
    full_description = models.TextField()
    details = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.category

class CashbackOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удален'),
        ('formed', 'Сформирован'),
        ('completed', 'Завершен'),
        ('rejected', 'Отклонен'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    creation_date = models.DateTimeField(default=timezone.now)
    formation_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders_created', on_delete=models.CASCADE)
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders_moderated', null=True, blank=True, on_delete=models.SET_NULL)
    month = models.CharField(max_length=20)  # Поле для месяца
    total_spent_month = models.PositiveIntegerField(null=True, blank=True)  # Поле для общей суммы

    def calculate_total_spent(self):
        if self.status == 'completed':
            total = 0
            for service in self.cashbackorderservice_set.all():
                # Извлекаем проценты из строки cashback_percentage_text, например '12%' -> 0.12
                percentage_text = service.service.cashback_percentage_text
                match = re.search(r'(\d+)', percentage_text)  # Ищем число в строке
                if match:
                    percentage = int(match.group(1)) / 100  # Преобразуем строку в число и делим на 100
                    cashback = service.total_spent * percentage  # Вычисляем сумму кешбэка
                    total += cashback  # Добавляем к общей сумме кешбэка
            self.total_spent_month = total  # Записываем итоговую сумму
            self.save(update_fields=['total_spent_month'])
        else:
            self.total_spent_month = None
            self.save(update_fields=['total_spent_month'])
    def __str__(self):
        return f"Заказ {self.id} от {self.creator.username}"

class CashbackOrderService(models.Model):
    order = models.ForeignKey(CashbackOrder, on_delete=models.CASCADE)
    service = models.ForeignKey(CashbackService, on_delete=models.CASCADE)
    total_spent = models.PositiveIntegerField(default=0)  # Поле для суммы

    class Meta:
        unique_together = ('order', 'service')

    def __str__(self):
        return f"Заказ {self.order.id} - Услуга {self.service.category}"

#авторизвция 4 лаба
class NewUserManager(UserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email) 
        user = self.model(email=email, **extra_fields) 
        user.set_password(password)
        user.save(using=self.db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(("email адрес"), unique=True)
    password = models.CharField(max_length=120, verbose_name="Пароль")    
    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")

    groups = models.ManyToManyField(
        'auth.Group',
        related_name="customuser_groups",  # Уникальное имя обратной связи
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name="customuser_permissions",  # Уникальное имя обратной связи
        blank=True
    )

    USERNAME_FIELD = 'email'

    objects =  NewUserManager()

    


































#     from django.db import models
# from django.contrib.auth.models import User
# from django.utils import timezone
# from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.conf import settings
# from rest_framework import serializers
# class CashbackService(models.Model):
#     STATUS_CHOICES = [
#         ('active', 'Активный'),
#         ('deleted', 'Удален'),
#     ]

#     category = models.CharField(max_length=255)
#     image_url = models.URLField()
#     cashback_percentage_text = models.CharField(max_length=255)
#     full_description = models.TextField()
#     details = models.TextField()
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

#     def __str__(self):
#         return self.category

# class CashbackOrder(models.Model):
#     STATUS_CHOICES = [
#         ('draft', 'Черновик'),
#         ('deleted', 'Удален'),
#         ('formed', 'Сформирован'),
#         ('completed', 'Завершен'),
#         ('rejected', 'Отклонен'),
#     ]

#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
#     creation_date = models.DateTimeField(default=timezone.now)
#     formation_date = models.DateTimeField(null=True, blank=True)
#     completion_date = models.DateTimeField(null=True, blank=True)
#     creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders_created', on_delete=models.CASCADE)
#     moderator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders_moderated', null=True, blank=True, on_delete=models.SET_NULL)
#     month = models.CharField(max_length=20)  # Поле для месяца
#     total_spent_month = models.PositiveIntegerField(null=True, blank=True)  # Поле для общей суммы

#     def calculate_total_spent(self):
#         if self.status == 'completed':
#             total = sum(service.total_spent for service in self.cashbackorderservice_set.all())
#             self.total_spent_month = total
#             self.save(update_fields=['total_spent_month'])
#         else:
#             self.total_spent_month = None
#             self.save(update_fields=['total_spent_month'])

#     def __str__(self):
#         return f"Заказ {self.id} от {self.creator.username}"

# class CashbackOrderService(models.Model):
#     order = models.ForeignKey(CashbackOrder, on_delete=models.CASCADE)
#     service = models.ForeignKey(CashbackService, on_delete=models.CASCADE)
#     total_spent = models.PositiveIntegerField(default=0)  # Поле для суммы

#     class Meta:
#         unique_together = ('order', 'service')

#     def __str__(self):
#         return f"Заказ {self.order.id} - Услуга {self.service.category}"

# #авторизвция 4 лаба
# class NewUserManager(UserManager):
#     def create_user(self,email,password=None, **extra_fields):
#         if not email:
#             raise ValueError('User must have an email address')
        
#         email = self.normalize_email(email) 
#         user = self.model(email=email, **extra_fields) 
#         user.set_password(password)
#         user.save(using=self.db)
#         return user

# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(("email адрес"), unique=True)
#     password = models.CharField(max_length=120, verbose_name="Пароль")    
#     is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
#     is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")

#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name="customuser_groups",  # Уникальное имя обратной связи
#         blank=True
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name="customuser_permissions",  # Уникальное имя обратной связи
#         blank=True
#     )

#     USERNAME_FIELD = 'email'

#     objects =  NewUserManager()


