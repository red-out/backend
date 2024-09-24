from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import date
from .models import CashbackService, CashbackOrder, CashbackOrderService
import random
import re

def all_cashback_services(request):
    # Получаем заявку в статусе 'draft'
    draft_order = CashbackOrder.objects.filter(creator=request.user, status='draft').first()
    
    # Количество карточек в текущей заявке
    transaction_count = 0
    if draft_order:
        transaction_count = CashbackOrderService.objects.filter(order=draft_order).count()

    # Обработка запроса поиска
    search_query = request.GET.get('cashback_categories', '')
    if search_query:
        filtered_services = CashbackService.objects.filter(category__icontains=search_query, status='active')
    else:
        filtered_services = CashbackService.objects.filter(status='active')

    current_report_id = draft_order.id if draft_order else None  # Получаем ID черновика, если он существует

    return render(request, 'index.html', {
        'data': {
            'current_date': date.today(),
            'services': filtered_services,
            'cart_item_count': transaction_count,
            'current_report_id': current_report_id,
            'search_query': search_query
        }
    })

def cashback_details(request, id):
    service = get_object_or_404(CashbackService, id=id)

    # Получаем или создаем черновик для текущего пользователя
    order, created = CashbackOrder.objects.get_or_create(
        creator=request.user,
        status='draft',
        defaults={'month': date.today().strftime("%B")}  # Пример месяца
    )

    # Если заявка только что создана, добавляем случайную услугу
    if created:
        random_service = random.choice(CashbackService.objects.filter(status='active'))
        CashbackOrderService.objects.create(
            order=order,
            service=random_service,
            total_spent=77777  # Устанавливаем потраченную сумму
        )

    return render(request, 'cashback_details.html', {'data': service})

def monthly_cashbacks_view(request, report_id):
    transactions_with_titles = []
    selected_report = get_object_or_404(CashbackOrder, id=report_id, creator=request.user, status__in=['draft', 'active'])

    for transaction in CashbackOrderService.objects.filter(order=selected_report):
        cashback_received = extract_cashback_percentage(transaction.service.cashback_percentage_text) * transaction.total_spent
        
        transactions_with_titles.append({
            'title': transaction.service.category,
            'category': transaction.service.category,
            'spent': transaction.total_spent,
            'cashback_received': round(cashback_received),  # Округляем до целого числа
            'image_url': transaction.service.image_url,
            'details_text': transaction.service.cashback_percentage_text,
            'cashback_percentage_text': transaction.service.cashback_percentage_text,
            'report_id': selected_report.id  
        })

    return render(request, 'monthly_cashbacks.html', {
        'data': {
            'categories_cashbacks': transactions_with_titles,
            'current_month': selected_report.month,
            'current_order_id': report_id  # Передаем ID заявки для удаления
        }
    })

def delete_cashback_order(request, report_id):
    if request.method == 'POST':
        order = get_object_or_404(CashbackOrder, id=report_id, creator=request.user)
        order.status = 'deleted'  # Изменение статуса на 'deleted'
        order.save()

        # Создаем новый черновик после удаления
        new_order = CashbackOrder.objects.create(creator=request.user, status='draft', month=date.today().strftime("%B"))

        # Добавляем случайную услугу в новую заявку
        random_service = random.choice(CashbackService.objects.filter(status='active'))
        CashbackOrderService.objects.create(
            order=new_order,
            service=random_service,
            total_spent=77777  # Устанавливаем потраченную сумму
        )

        return HttpResponseRedirect(reverse('home'))  # Перенаправление на главную страницу

def extract_cashback_percentage(cashback_percentage_text):
    match = re.search(r'(\d+)%', cashback_percentage_text)
    if match:
        return int(match.group(1)) / 100
    return 0

# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponseRedirect
# from django.urls import reverse
# from datetime import date
# from .models import CashbackService, CashbackOrder, CashbackOrderService
# import re

# def all_cashback_services(request):
#     # Получаем или создаем заявку в статусе 'draft'
#     draft_order, created = CashbackOrder.objects.get_or_create(
#         creator=request.user,
#         status='draft',
#         defaults={'month': date.today().strftime("%B")}  # Пример месяца
#     )

#     # Количество карточек в текущем черновике
#     transaction_count = CashbackOrderService.objects.filter(order=draft_order).count()

#     # Обработка запроса поиска
#     search_query = request.GET.get('cashback_categories', '')
#     if search_query:
#         filtered_services = CashbackService.objects.filter(category__icontains=search_query, status='active')
#     else:
#         filtered_services = CashbackService.objects.filter(status='active')

#     current_report_id = draft_order.id if draft_order else None  # Получаем ID черновика, если он существует

#     return render(request, 'index.html', {
#         'data': {
#             'current_date': date.today(),
#             'services': filtered_services,
#             'cart_item_count': transaction_count,
#             'current_report_id': current_report_id,
#             'search_query': search_query
#         }
#     })

# def cashback_details(request, id):
#     service = get_object_or_404(CashbackService, id=id)

#     # Получаем или создаем черновик для текущего пользователя
#     order, created = CashbackOrder.objects.get_or_create(
#         creator=request.user,
#         status='draft',
#         defaults={'month': date.today().strftime("%B")}  # Пример месяца
#     )

#     # Проверяем, была ли услуга уже добавлена в заявку
#     cashback_order_service, created_service = CashbackOrderService.objects.get_or_create(
#         order=order,
#         service=service,
#         defaults={'total_spent': 0}  # Устанавливаем начальное значение
#     )

#     if not created_service:
#         # Если услуга уже есть, обновляем total_spent
#         cashback_order_service.total_spent += 100  # Пример добавления суммы
#         cashback_order_service.save()

#     return render(request, 'cashback_details.html', {'data': service})

# def monthly_cashbacks_view(request, report_id):
#     transactions_with_titles = []
#     selected_report = get_object_or_404(CashbackOrder, id=report_id, creator=request.user, status__in=['draft', 'active'])

#     # Получаем услуги, относящиеся к данной заявке
#     for transaction in CashbackOrderService.objects.filter(order=selected_report):
#         cashback_received = extract_cashback_percentage(transaction.service.cashback_percentage_text) * transaction.total_spent
        
#         transactions_with_titles.append({
#             'title': transaction.service.category,
#             'category': transaction.service.category,
#             'spent': transaction.total_spent,
#             'cashback_received': round(cashback_received),  # Округляем до целого числа
#             'image_url': transaction.service.image_url,
#             'details_text': transaction.service.cashback_percentage_text,
#             'cashback_percentage_text': transaction.service.cashback_percentage_text,
#             'report_id': selected_report.id  
#         })

#     return render(request, 'monthly_cashbacks.html', {
#         'data': {
#             'categories_cashbacks': transactions_with_titles,
#             'current_month': selected_report.month,
#             'current_order_id': report_id  # Передаем ID заявки для удаления
#         }
#     })

# def delete_cashback_order(request, report_id):
#     if request.method == 'POST':
#         order = get_object_or_404(CashbackOrder, id=report_id, creator=request.user)
#         order.status = 'deleted'  # Изменение статуса на 'deleted'
#         order.save()
#         return HttpResponseRedirect(reverse('home'))  # Перенаправление на главную страницу

# def extract_cashback_percentage(cashback_percentage_text):
#     match = re.search(r'(\d+)%', cashback_percentage_text)
#     if match:
#         return int(match.group(1)) / 100
#     return 0

