# Generated by Django 5.1.1 on 2024-09-23 23:09

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CashbackService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=255)),
                ('image_url', models.URLField()),
                ('cashback_percentage_text', models.CharField(max_length=255)),
                ('full_description', models.TextField()),
                ('details', models.TextField()),
                ('status', models.CharField(choices=[('active', 'Активный'), ('deleted', 'Удален')], default='active', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='CashbackOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('draft', 'Черновик'), ('deleted', 'Удален'), ('formed', 'Сформирован'), ('completed', 'Завершен'), ('rejected', 'Отклонен')], default='draft', max_length=10)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('formation_date', models.DateTimeField(blank=True, null=True)),
                ('completion_date', models.DateTimeField(blank=True, null=True)),
                ('month', models.CharField(max_length=20)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders_created', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CashbackOrderService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_spent', models.PositiveIntegerField(default=0)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.cashbackorder')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.cashbackservice')),
            ],
            options={
                'unique_together': {('order', 'service')},
            },
        ),
    ]
