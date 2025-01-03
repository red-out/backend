# Generated by Django 5.1.1 on 2024-11-05 11:25

import django.db.models.deletion
import django.utils.timezone
import tasks.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
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
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email адрес')),
                ('password', models.CharField(max_length=120, verbose_name='Пароль')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Является ли пользователь менеджером?')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='Является ли пользователь админом?')),
                ('groups', models.ManyToManyField(blank=True, related_name='customuser_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='customuser_permissions', to='auth.permission')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', tasks.models.NewUserManager()),
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
                ('total_spent_month', models.PositiveIntegerField(blank=True, null=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders_created', to=settings.AUTH_USER_MODEL)),
                ('moderator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_moderated', to=settings.AUTH_USER_MODEL)),
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
