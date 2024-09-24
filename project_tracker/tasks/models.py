from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
    creator = models.ForeignKey(User, related_name='orders_created', on_delete=models.CASCADE)
    month = models.CharField(max_length=20)  # Поле для месяца
    total_spent_month = models.PositiveIntegerField(null=True, blank=True)  # Поле для общей суммы

    def calculate_total_spent(self):
        if self.status == 'completed':
            total = sum(service.total_spent for service in self.cashbackorderservice_set.all())
            self.total_spent_month = total
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

